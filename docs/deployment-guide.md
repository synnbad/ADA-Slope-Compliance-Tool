# 🚀 AWS MVP Deployment Guide

Complete step-by-step guide to deploy the ADA Slope Compliance Tool AWS MVP.

## Prerequisites

### 1. AWS Account Setup
- AWS Account with appropriate permissions
- AWS CLI installed and configured
- Terraform installed (≥1.5.0)
- Docker installed and running
- Git and GitHub account

### 2. Required AWS Permissions
Your AWS user/role needs these permissions:
- ECR: Full access for container registry
- Lambda: Full access for function deployment
- API Gateway: Full access for HTTP APIs
- S3: Full access for static hosting
- DynamoDB: Full access for job storage
- IAM: Create roles and policies

## 🏗️ Step 1: Infrastructure Setup

### Clone and Navigate
```bash
git clone https://github.com/synnbad/ADA-Slope-Compliance-Tool.git
cd ADA-Slope-Compliance-Tool
git checkout feature/aws-mvp-scaffold
```

### Set Environment Variables
```bash
# Required variables
export AWS_REGION=us-east-1
export PROJECT_NAME=ada-slope
export BUCKET_NAME=ada-slope-demo-$(date +%s)  # Must be globally unique
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
```

## 🐳 Step 2: Build and Push Docker Image

### Create ECR Repository
```bash
aws ecr create-repository --repository-name ${PROJECT_NAME}-api --region ${AWS_REGION} || echo "Repository already exists"
```

### Build and Push Image
```bash
cd backend

# Get ECR login
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com

# Build image
docker build -t ${PROJECT_NAME}-api .

# Tag and push
docker tag ${PROJECT_NAME}-api:latest ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest

cd ..
```

## 🏢 Step 3: Deploy Infrastructure with Terraform

### Initialize Terraform
```bash
cd infra
terraform init
```

### Plan Infrastructure
```bash
terraform plan \
  -var="bucket_name=${BUCKET_NAME}" \
  -var="lambda_image_uri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest"
```

### Deploy Infrastructure
```bash
terraform apply -auto-approve \
  -var="bucket_name=${BUCKET_NAME}" \
  -var="lambda_image_uri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest"
```

### Get API URL
```bash
export API_URL=$(terraform output -raw http_api_url)
echo "API Gateway URL: ${API_URL}"
cd ..
```

## 🌐 Step 4: Deploy Frontend

### Configure Frontend
```bash
cd frontend

# Update API endpoint in index.html (replace with your API Gateway URL)
sed -i 's|location.origin.replace(/\/$/, "") + "/api"|"'${API_URL}'"|g' index.html

# Upload to S3
aws s3 sync . s3://${BUCKET_NAME} --exclude "*.md"

# Configure S3 for static website hosting
aws s3 website s3://${BUCKET_NAME} --index-document index.html

echo "Frontend URL: http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"
cd ..
```

## 🧪 Step 5: Test the Deployment

### Create Test Data
```bash
# Generate synthetic test DEMs
python scripts/fetch_demo_data.py synthetic --pattern flat --out /tmp/flat_test.tif --shape 50 50
python scripts/fetch_demo_data.py synthetic --pattern plane --slope-pct 8 --axis x --out /tmp/steep_test.tif --shape 50 50
```

### Test API Endpoints
```bash
echo "Testing API endpoints..."

# Test 1: Upload flat DEM (should pass ADA compliance)
echo "1. Testing flat DEM (should pass):"
FLAT_RESPONSE=$(curl -s -F "file=@/tmp/flat_test.tif" ${API_URL}/upload)
FLAT_JOB_ID=$(echo $FLAT_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
echo "Job ID: $FLAT_JOB_ID"

if [ ! -z "$FLAT_JOB_ID" ]; then
    echo "Results:"
    curl -s ${API_URL}/results/${FLAT_JOB_ID} | python -m json.tool
fi

echo -e "\n" 

# Test 2: Upload steep DEM (should fail ADA compliance)
echo "2. Testing steep DEM (should fail):"
STEEP_RESPONSE=$(curl -s -F "file=@/tmp/steep_test.tif" ${API_URL}/upload)
STEEP_JOB_ID=$(echo $STEEP_RESPONSE | grep -o '"job_id":"[^"]*"' | cut -d'"' -f4)
echo "Job ID: $STEEP_JOB_ID"

if [ ! -z "$STEEP_JOB_ID" ]; then
    echo "Results:"
    curl -s ${API_URL}/results/${STEEP_JOB_ID} | python -m json.tool
fi
```

### Test Frontend
```bash
echo -e "\nFrontend available at:"
echo "http://${BUCKET_NAME}.s3-website-${AWS_REGION}.amazonaws.com"
echo -e "\nTry uploading the test files generated in /tmp/"
```

## 📊 Step 6: Monitoring and Validation

### Check Lambda Logs
```bash
# Get latest log stream
LOG_GROUP="/aws/lambda/${PROJECT_NAME}-api"
aws logs describe-log-streams --log-group-name $LOG_GROUP --order-by LastEventTime --descending --limit 1

# View recent logs (replace LOG_STREAM with actual stream name)
# aws logs get-log-events --log-group-name $LOG_GROUP --log-stream-name LOG_STREAM
```

### Validate Infrastructure
```bash
echo "Infrastructure Validation:"
echo "✓ ECR Repository: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api"
echo "✓ Lambda Function: ${PROJECT_NAME}-api"
echo "✓ API Gateway: ${API_URL}"
echo "✓ S3 Bucket: ${BUCKET_NAME}"
echo "✓ DynamoDB Table: ${PROJECT_NAME}-jobs"
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Docker Build Fails
```bash
# Check if Docker is running
docker info

# Clean Docker cache
docker system prune -f

# Rebuild with no cache
docker build --no-cache -t ${PROJECT_NAME}-api backend/
```

#### 2. ECR Push Permission Denied
```bash
# Re-authenticate with ECR
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

#### 3. Lambda Function Timeout
- Check CloudWatch logs: `/aws/lambda/${PROJECT_NAME}-api`
- Consider increasing timeout in `infra/main.tf` (currently 60s)
- Check DEM file size (Lambda has 512MB memory limit)

#### 4. API Gateway 502 Error
- Verify Lambda function is healthy
- Check Lambda environment variables
- Ensure Lambda has proper IAM permissions

#### 5. CORS Issues
```bash
# Add CORS headers to API Gateway if needed
# Current setup should handle CORS automatically
```

### Health Check Commands
```bash
# Check API health
curl -I ${API_URL}/docs  # Should return FastAPI docs

# Check Lambda function
aws lambda invoke --function-name ${PROJECT_NAME}-api --payload '{}' /tmp/lambda-test.json
cat /tmp/lambda-test.json
```

## 🔄 CI/CD Setup (Optional)

### GitHub Actions Setup
1. Create GitHub repository secrets:
   - `AWS_ROLE_TO_ASSUME`: IAM role ARN for OIDC
   - Configure OIDC provider in AWS IAM

2. The following workflows are already configured:
   - `python-ci.yml`: Runs on PR (testing, linting)
   - `build-and-push-ecr.yml`: Runs on tags (Docker build)
   - `terraform-plan.yml`: Runs on infra changes

### Automated Deployment
```bash
# Tag a release to trigger ECR build
git tag v1.0.0
git push origin v1.0.0
```

## 🧹 Cleanup

### Destroy Infrastructure
```bash
cd infra

# Destroy all AWS resources
terraform destroy -auto-approve \
  -var="bucket_name=${BUCKET_NAME}" \
  -var="lambda_image_uri=${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${PROJECT_NAME}-api:latest"

# Clean up ECR repository
aws ecr delete-repository --repository-name ${PROJECT_NAME}-api --force

# Remove local test files
rm -f /tmp/*_test.tif
```

## 🎯 Success Criteria

Your deployment is successful when:
- ✅ API Gateway returns valid responses
- ✅ Frontend loads and can upload files  
- ✅ Flat DEM shows 0% violations (pass=true)
- ✅ Steep DEM shows >0% violations (pass=false)
- ✅ Lambda logs show successful processing
- ✅ All Terraform resources deployed without errors

## 📞 Support

For issues with this deployment:
1. Check the troubleshooting section above
2. Review CloudWatch logs for detailed error messages
3. Verify all prerequisites are met
4. Ensure AWS permissions are correctly configured

**Next Steps**: Once deployed, you can enhance the MVP with:
- DynamoDB job persistence
- S3 artifact storage  
- Enhanced UI with progress indicators
- Batch processing capabilities
- Additional ADA compliance metrics
