# ADA Slope Compliance Tool - AWS MVP Deployment Script (PowerShell)
# This script automates the complete deployment process for Windows

param(
    [string]$Region = "us-east-1",
    [switch]$SkipTests,
    [switch]$Help
)

if ($Help) {
    Write-Host @"
🚀 ADA Slope Compliance Tool - AWS MVP Deployment (PowerShell)

USAGE:
    .\scripts\deploy.ps1 [-Region <region>] [-SkipTests] [-Help]

PARAMETERS:
    -Region     AWS region to deploy to (default: us-east-1)
    -SkipTests  Skip the deployment testing phase
    -Help       Show this help message

EXAMPLES:
    .\scripts\deploy.ps1
    .\scripts\deploy.ps1 -Region us-west-2
    .\scripts\deploy.ps1 -SkipTests

"@
    exit 0
}

# Set error action preference
$ErrorActionPreference = "Stop"

Write-Host "🏗️ ADA Slope Compliance Tool - AWS MVP Deployment" -ForegroundColor Blue
Write-Host "=================================================" -ForegroundColor Blue
Write-Host ""

# Helper functions for colored output
function Write-Info($message) {
    Write-Host "ℹ️  $message" -ForegroundColor Cyan
}

function Write-Success($message) {
    Write-Host "✅ $message" -ForegroundColor Green
}

function Write-Warning($message) {
    Write-Host "⚠️  $message" -ForegroundColor Yellow
}

function Write-Error($message) {
    Write-Host "❌ $message" -ForegroundColor Red
}

# Check prerequisites
function Test-Prerequisites {
    Write-Info "Checking prerequisites..."
    
    # Check AWS CLI
    try {
        $null = Get-Command aws -ErrorAction Stop
    } catch {
        Write-Error "AWS CLI not found. Please install AWS CLI first."
        throw
    }
    
    # Check Docker
    try {
        $null = Get-Command docker -ErrorAction Stop
    } catch {
        Write-Error "Docker not found. Please install Docker first."
        throw
    }
    
    # Check Terraform
    try {
        $null = Get-Command terraform -ErrorAction Stop
    } catch {
        Write-Error "Terraform not found. Please install Terraform first."
        throw
    }
    
    # Check AWS credentials
    try {
        aws sts get-caller-identity --output text | Out-Null
    } catch {
        Write-Error "AWS credentials not configured. Run 'aws configure' first."
        throw
    }
    
    # Check Docker daemon
    try {
        docker info | Out-Null
    } catch {
        Write-Error "Docker daemon not running. Please start Docker first."
        throw
    }
    
    Write-Success "All prerequisites met"
}

# Set environment variables
function Initialize-Environment {
    Write-Info "Setting up environment variables..."
    
    $script:PROJECT_NAME = "ada-slope"
    $script:BUCKET_NAME = "ada-slope-demo-$(Get-Date -UFormat %s -Millisecond 0)"
    $script:AWS_REGION = $Region
    
    try {
        $script:AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text).Trim()
    } catch {
        Write-Error "Failed to get AWS Account ID"
        throw
    }
    
    Write-Info "Environment setup:"
    Write-Info "  AWS Region: $script:AWS_REGION"
    Write-Info "  Project Name: $script:PROJECT_NAME"
    Write-Info "  S3 Bucket: $script:BUCKET_NAME"
    Write-Info "  AWS Account: $script:AWS_ACCOUNT_ID"
}

# Create ECR repository
function New-EcrRepository {
    Write-Info "Creating ECR repository..."
    
    try {
        aws ecr create-repository --repository-name "$script:PROJECT_NAME-api" --region $script:AWS_REGION --image-scanning-configuration scanOnPush=true 2>$null | Out-Null
    } catch {
        Write-Warning "Repository may already exist"
    }
    
    Write-Success "ECR repository ready"
}

# Build and push Docker image
function Invoke-ImageBuildAndPush {
    Write-Info "Building and pushing Docker image..."
    
    Push-Location backend
    
    try {
        # Authenticate with ECR
        Write-Info "Authenticating with ECR..."
        $loginCommand = aws ecr get-login-password --region $script:AWS_REGION
        $loginCommand | docker login --username AWS --password-stdin "$script:AWS_ACCOUNT_ID.dkr.ecr.$script:AWS_REGION.amazonaws.com"
        
        # Build image
        Write-Info "Building Docker image..."
        docker build -t "$script:PROJECT_NAME-api" . --quiet
        
        # Tag image
        docker tag "${script:PROJECT_NAME}-api:latest" "$script:AWS_ACCOUNT_ID.dkr.ecr.$script:AWS_REGION.amazonaws.com/${script:PROJECT_NAME}-api:latest"
        
        # Push image
        Write-Info "Pushing image to ECR..."
        docker push "$script:AWS_ACCOUNT_ID.dkr.ecr.$script:AWS_REGION.amazonaws.com/${script:PROJECT_NAME}-api:latest" --quiet
        
        Write-Success "Docker image built and pushed"
    }
    finally {
        Pop-Location
    }
}

# Deploy infrastructure with Terraform
function Invoke-InfrastructureDeployment {
    Write-Info "Deploying infrastructure with Terraform..."
    
    Push-Location infra
    
    try {
        # Initialize Terraform
        Write-Info "Initializing Terraform..."
        terraform init -input=$false | Out-Null
        
        # Plan infrastructure
        Write-Info "Planning infrastructure..."
        terraform plan -var="bucket_name=$script:BUCKET_NAME" -var="lambda_image_uri=$script:AWS_ACCOUNT_ID.dkr.ecr.$script:AWS_REGION.amazonaws.com/${script:PROJECT_NAME}-api:latest" -out=tfplan -input=$false | Out-Null
        
        # Apply infrastructure
        Write-Info "Deploying infrastructure..."
        terraform apply -auto-approve tfplan | Out-Null
        
        # Get API URL
        $script:API_URL = (terraform output -raw http_api_url).Trim()
        
        Write-Success "Infrastructure deployed"
        Write-Info "API Gateway URL: $script:API_URL"
    }
    finally {
        Pop-Location
    }
}

# Deploy frontend to S3
function Invoke-FrontendDeployment {
    Write-Info "Deploying frontend to S3..."
    
    Push-Location frontend
    
    try {
        # Update API endpoint in HTML
        $htmlContent = Get-Content index.html -Raw
        $htmlContent = $htmlContent -replace 'location\.origin\.replace\(/\\\/$/, ""\) \+ "/api"', """$script:API_URL"""
        $htmlContent | Set-Content index.html -NoNewline
        
        # Upload to S3
        aws s3 sync . "s3://$script:BUCKET_NAME" --exclude "*.md" --quiet
        
        # Configure static website hosting
        aws s3 website "s3://$script:BUCKET_NAME" --index-document index.html | Out-Null
        
        # Make bucket public for website hosting
        $policy = @"
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::$script:BUCKET_NAME/*"
        }
    ]
}
"@
        $policy | aws s3api put-bucket-policy --bucket $script:BUCKET_NAME --policy file:///dev/stdin
        
        $script:FRONTEND_URL = "http://$script:BUCKET_NAME.s3-website-$script:AWS_REGION.amazonaws.com"
        
        Write-Success "Frontend deployed"
        Write-Info "Frontend URL: $script:FRONTEND_URL"
    }
    finally {
        Pop-Location
    }
}

# Test deployment with synthetic data
function Test-Deployment {
    if ($SkipTests) {
        Write-Info "Skipping deployment tests as requested"
        return
    }
    
    Write-Info "Testing deployment with synthetic data..."
    
    # Generate test DEMs
    python scripts/fetch_demo_data.py synthetic --pattern flat --out C:\temp\flat_test.tif --shape 50 50 2>$null
    python scripts/fetch_demo_data.py synthetic --pattern plane --slope-pct 8 --axis x --out C:\temp\steep_test.tif --shape 50 50 2>$null
    
    # Wait for Lambda cold start
    Start-Sleep -Seconds 10
    
    # Test flat DEM (should pass)
    Write-Info "Testing flat DEM (should pass ADA compliance)..."
    try {
        $flatResponse = curl.exe -s -F "file=@C:\temp\flat_test.tif" "$script:API_URL/upload"
        
        if ($flatResponse -match '"job_id":"([^"]*)"') {
            $flatJobId = $Matches[1]
            Write-Info "Flat DEM Job ID: $flatJobId"
            
            # Wait for processing
            Start-Sleep -Seconds 5
            
            $flatResult = curl.exe -s "$script:API_URL/results/$flatJobId"
            if ($flatResult -match '"pass":true') {
                Write-Success "Flat DEM test passed (ADA compliant)"
            } else {
                Write-Warning "Flat DEM test result: $flatResult"
            }
        } else {
            Write-Error "Failed to upload flat DEM: $flatResponse"
        }
    } catch {
        Write-Warning "Flat DEM test failed: $($_.Exception.Message)"
    }
    
    # Test steep DEM (should fail)
    Write-Info "Testing steep DEM (should fail ADA compliance)..."
    try {
        $steepResponse = curl.exe -s -F "file=@C:\temp\steep_test.tif" "$script:API_URL/upload"
        
        if ($steepResponse -match '"job_id":"([^"]*)"') {
            $steepJobId = $Matches[1]
            Write-Info "Steep DEM Job ID: $steepJobId"
            
            # Wait for processing
            Start-Sleep -Seconds 5
            
            $steepResult = curl.exe -s "$script:API_URL/results/$steepJobId"
            if ($steepResult -match '"pass":false') {
                Write-Success "Steep DEM test passed (correctly failed ADA compliance)"
            } else {
                Write-Warning "Steep DEM test result: $steepResult"
            }
        } else {
            Write-Error "Failed to upload steep DEM: $steepResponse"
        }
    } catch {
        Write-Warning "Steep DEM test failed: $($_.Exception.Message)"
    }
    
    # Clean up test files
    Remove-Item -Path C:\temp\flat_test.tif, C:\temp\steep_test.tif -Force -ErrorAction SilentlyContinue
    
    Write-Success "Deployment testing completed"
}

# Display final summary
function Show-Summary {
    Write-Host ""
    Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
    Write-Host "======================" -ForegroundColor Green
    Write-Host ""
    Write-Success "AWS MVP successfully deployed"
    Write-Host ""
    Write-Host "📊 Deployment Summary:"
    Write-Host "  • API Gateway: $script:API_URL"
    Write-Host "  • Frontend: $script:FRONTEND_URL"
    Write-Host "  • ECR Repository: $script:AWS_ACCOUNT_ID.dkr.ecr.$script:AWS_REGION.amazonaws.com/${script:PROJECT_NAME}-api"
    Write-Host "  • Lambda Function: ${script:PROJECT_NAME}-api"
    Write-Host "  • S3 Bucket: $script:BUCKET_NAME"
    Write-Host "  • DynamoDB Table: ${script:PROJECT_NAME}-jobs"
    Write-Host ""
    Write-Host "🧪 Test Your Deployment:"
    Write-Host "  1. Visit the frontend URL above"
    Write-Host "  2. Upload a DEM file (GeoTIFF format)"
    Write-Host "  3. View the ADA compliance analysis results"
    Write-Host ""
    Write-Host "📚 Next Steps:"
    Write-Host "  • Review CloudWatch logs: /aws/lambda/${script:PROJECT_NAME}-api"
    Write-Host "  • Monitor costs in AWS Billing Dashboard"
    Write-Host "  • Consider setting up custom domain with Route53"
    Write-Host "  • Implement additional ADA metrics as needed"
    Write-Host ""
    Write-Info "Deployment script completed successfully!"
}

# Error handling and cleanup
function Invoke-Cleanup {
    Write-Warning "Deployment failed. Cleaning up partial resources..."
    
    # Clean up Docker images
    try {
        docker rmi -f "$script:PROJECT_NAME-api" 2>$null
        docker rmi -f "$script:AWS_ACCOUNT_ID.dkr.ecr.$script:AWS_REGION.amazonaws.com/${script:PROJECT_NAME}-api:latest" 2>$null
    } catch {}
    
    # Clean up test files
    Remove-Item -Path C:\temp\flat_test.tif, C:\temp\steep_test.tif -Force -ErrorAction SilentlyContinue
    
    Write-Info "Partial cleanup completed. You may need to manually clean up AWS resources."
}

# Main deployment flow
function Start-Deployment {
    try {
        Write-Host "Starting deployment process..." -ForegroundColor Blue
        Write-Host ""
        
        Test-Prerequisites
        Initialize-Environment
        New-EcrRepository
        Invoke-ImageBuildAndPush
        Invoke-InfrastructureDeployment
        Invoke-FrontendDeployment
        Test-Deployment
        Show-Summary
    }
    catch {
        Write-Error "Deployment failed: $($_.Exception.Message)"
        Invoke-Cleanup
        throw
    }
}

# Execute main deployment
Start-Deployment
