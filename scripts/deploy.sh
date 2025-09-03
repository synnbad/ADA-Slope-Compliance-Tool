#!/bin/bash
set -e

# 🚀 ADA Slope Compliance Tool - AWS MVP Deployment Script
# This script automates the complete deployment process

echo "🏗️ ADA Slope Compliance Tool - AWS MVP Deployment"
echo "================================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI not found. Please install AWS CLI first."
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker not found. Please install Docker first."
        exit 1
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform not found. Please install Terraform first."
        exit 1
    fi
    
    # Check AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_error "AWS credentials not configured. Run 'aws configure' first."
        exit 1
    fi
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        log_error "Docker daemon not running. Please start Docker first."
        exit 1
    fi
    
    log_success "All prerequisites met"
}

# Set environment variables
setup_environment() {
    log_info "Setting up environment variables..."
    
    # Prompt for region if not set
    if [ -z "$AWS_REGION" ]; then
        read -p "Enter AWS region (default: us-east-1): " AWS_REGION
        export AWS_REGION=${AWS_REGION:-us-east-1}
    fi
    
    # Set project variables
    export PROJECT_NAME=ada-slope
    export BUCKET_NAME=ada-slope-demo-$(date +%s)
    export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
    
    log_info "Environment setup:"
    log_info "  AWS Region: $AWS_REGION"
    log_info "  Project Name: $PROJECT_NAME"
    log_info "  S3 Bucket: $BUCKET_NAME"
    log_info "  AWS Account: $AWS_ACCOUNT_ID"
}

# Create ECR repository
create_ecr_repo() {
    log_info "Creating ECR repository..."
    
    aws ecr create-repository \
        --repository-name ${PROJECT_NAME}-api \
        --region ${AWS_REGION} \
        --image-scanning-configuration scanOnPush=true \
        > /dev/null 2>&1 || log_warning "Repository may already exist"
    
    log_success "ECR repository ready"
}

# Build and push Docker image
build_and_push_image() {
    log_info "Building and pushing Docker image..."
    
    cd backend
    
    # Authenticate with ECR
    log_info "Authenticating with ECR..."
    aws ecr get-login-password --region ${AWS_REGION} | \
        docker login --username AWS --password-stdin \
        ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
    
    # Build image
    log_info "Building Docker image..."
    docker build -t ${PROJECT_NAME}-api . --quiet
    
    # Tag image
    docker tag ${PROJECT_NAME}-api:latest \
        ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest
    
    # Push image
    log_info "Pushing image to ECR..."
    docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest --quiet
    
    cd ..
    log_success "Docker image built and pushed"
}

# Deploy infrastructure with Terraform
deploy_infrastructure() {
    log_info "Deploying infrastructure with Terraform..."
    
    cd infra
    
    # Initialize Terraform
    log_info "Initializing Terraform..."
    terraform init -input=false > /dev/null
    
    # Plan infrastructure
    log_info "Planning infrastructure..."
    terraform plan \
        -var="bucket_name=${BUCKET_NAME}" \
        -var="lambda_image_uri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest" \
        -out=tfplan \
        -input=false > /dev/null
    
    # Apply infrastructure
    log_info "Deploying infrastructure..."
    terraform apply -auto-approve tfplan > /dev/null
    
    # Get API URL
    export API_URL=$(terraform output -raw http_api_url)
    
    cd ..
    log_success "Infrastructure deployed"
    log_info "API Gateway URL: $API_URL"
}

# Deploy frontend to S3
deploy_frontend() {
    log_info "Deploying frontend to S3..."
    
    cd frontend
    
    # Update API endpoint in HTML
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's|location.origin.replace(/\/$/, "") + "/api"|"'${API_URL}'"|g' index.html
    else
        # Linux
        sed -i 's|location.origin.replace(/\/$/, "") + "/api"|"'${API_URL}'"|g' index.html
    fi
    
    # Upload to S3
    aws s3 sync . s3://${BUCKET_NAME} --exclude "*.md" --quiet
    
    # Configure static website hosting
    aws s3 website s3://${BUCKET_NAME} --index-document index.html > /dev/null
    
    # Make bucket public for website hosting
    aws s3api put-bucket-policy --bucket ${BUCKET_NAME} --policy '{
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": "arn:aws:s3:::'${BUCKET_NAME}'/*"
            }
        ]
    }' > /dev/null
    
    export FRONTEND_URL="http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"
    
    cd ..
    log_success "Frontend deployed"
    log_info "Frontend URL: $FRONTEND_URL"
}

# Generate and test with synthetic data
test_deployment() {
    log_info "Testing deployment with synthetic data..."
    
    # Generate test DEMs
    python scripts/fetch_demo_data.py synthetic --pattern flat --out /tmp/flat_test.tif --shape 50 50 2>/dev/null
    python scripts/fetch_demo_data.py synthetic --pattern plane --slope-pct 8 --axis x --out /tmp/steep_test.tif --shape 50 50 2>/dev/null
    
    # Wait for Lambda cold start
    sleep 10
    
    # Test flat DEM (should pass)
    log_info "Testing flat DEM (should pass ADA compliance)..."
    FLAT_RESPONSE=$(curl -s -F "file=@/tmp/flat_test.tif" ${API_URL}/upload)
    
    if echo "$FLAT_RESPONSE" | grep -q "job_id"; then
        FLAT_JOB_ID=$(echo $FLAT_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
        log_info "Flat DEM Job ID: $FLAT_JOB_ID"
        
        # Wait for processing
        sleep 5
        
        FLAT_RESULT=$(curl -s ${API_URL}/results/${FLAT_JOB_ID})
        if echo "$FLAT_RESULT" | grep -q '"pass":true'; then
            log_success "Flat DEM test passed (ADA compliant)"
        else
            log_warning "Flat DEM test result: $FLAT_RESULT"
        fi
    else
        log_error "Failed to upload flat DEM: $FLAT_RESPONSE"
    fi
    
    # Test steep DEM (should fail)  
    log_info "Testing steep DEM (should fail ADA compliance)..."
    STEEP_RESPONSE=$(curl -s -F "file=@/tmp/steep_test.tif" ${API_URL}/upload)
    
    if echo "$STEEP_RESPONSE" | grep -q "job_id"; then
        STEEP_JOB_ID=$(echo $STEEP_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
        log_info "Steep DEM Job ID: $STEEP_JOB_ID"
        
        # Wait for processing
        sleep 5
        
        STEEP_RESULT=$(curl -s ${API_URL}/results/${STEEP_JOB_ID})
        if echo "$STEEP_RESULT" | grep -q '"pass":false'; then
            log_success "Steep DEM test passed (correctly failed ADA compliance)"
        else
            log_warning "Steep DEM test result: $STEEP_RESULT"
        fi
    else
        log_error "Failed to upload steep DEM: $STEEP_RESPONSE"
    fi
    
    # Clean up test files
    rm -f /tmp/flat_test.tif /tmp/steep_test.tif
    
    log_success "Deployment testing completed"
}

# Display final summary
show_summary() {
    echo ""
    echo "🎉 Deployment Complete!"
    echo "======================"
    echo ""
    log_success "AWS MVP successfully deployed"
    echo ""
    echo "📊 Deployment Summary:"
    echo "  • API Gateway: $API_URL"
    echo "  • Frontend: $FRONTEND_URL"
    echo "  • ECR Repository: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api"
    echo "  • Lambda Function: ${PROJECT_NAME}-api"
    echo "  • S3 Bucket: $BUCKET_NAME"
    echo "  • DynamoDB Table: ${PROJECT_NAME}-jobs"
    echo ""
    echo "🧪 Test Your Deployment:"
    echo "  1. Visit the frontend URL above"
    echo "  2. Upload a DEM file (GeoTIFF format)"
    echo "  3. View the ADA compliance analysis results"
    echo ""
    echo "📚 Next Steps:"
    echo "  • Review CloudWatch logs: /aws/lambda/${PROJECT_NAME}-api"
    echo "  • Monitor costs in AWS Billing Dashboard"
    echo "  • Consider setting up custom domain with Route53"
    echo "  • Implement additional ADA metrics as needed"
    echo ""
    log_info "Deployment script completed successfully!"
}

# Error handling
cleanup_on_error() {
    log_error "Deployment failed. Cleaning up partial resources..."
    
    # Clean up Docker images
    docker rmi -f ${PROJECT_NAME}-api 2>/dev/null || true
    docker rmi -f ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest 2>/dev/null || true
    
    # Clean up test files
    rm -f /tmp/flat_test.tif /tmp/steep_test.tif 2>/dev/null || true
    
    log_info "Partial cleanup completed. You may need to manually clean up AWS resources."
    exit 1
}

# Set up error handling
trap cleanup_on_error ERR

# Main deployment flow
main() {
    echo "Starting deployment process..."
    echo ""
    
    check_prerequisites
    setup_environment
    create_ecr_repo
    build_and_push_image
    deploy_infrastructure
    deploy_frontend
    test_deployment
    show_summary
}

# Check if script is being sourced or executed
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
