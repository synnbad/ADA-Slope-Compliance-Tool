# ADA Slope Compliance Tool — AWS MVP

Minimal FastAPI API on AWS Lambda (container) + API Gateway with a static S3 frontend. Upload a DEM GeoTIFF, compute slope, and see ADA-relevant summaries.

## Quickstart (Deployment)

### 1) Build & Push the Lambda Image
```bash
cd backend
aws ecr create-repository --repository-name ada-slope-api || true
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION=us-east-1
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com
docker build -t ada-slope-api .
docker tag ada-slope-api:latest $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ada-slope-api:latest
docker push $ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ada-slope-api:latest
```

### 2) Provision Infra (Terraform)
```bash
cd ../infra
terraform init
terraform apply -auto-approve \
  -var="bucket_name=YOUR_UNIQUE_BUCKET" \
  -var="lambda_image_uri=$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/ada-slope-api:latest"
```

### 3) Deploy Frontend
```bash
cd ../frontend
aws s3 sync . s3://YOUR_UNIQUE_BUCKET
```

### 4) Smoke Test
```bash
API=$(terraform -chdir=../infra output -raw http_api_url)

# Create a tiny synthetic DEM
python ../scripts/fetch_demo_data.py synthetic --pattern flat --out /tmp/flat_20x20.tif --shape 20 20

# Upload
curl -F "file=@/tmp/flat_20x20.tif" "$API/upload"
# => {"job_id":"..."}

# Results
curl "$API/results/JOB_ID"
```

## Development & Tests
```bash
pip install -r backend/requirements.txt
pip install ruff black mypy pytest pytest-cov hypothesis
pytest
```

## Architecture

See docs/architecture.mmd (Mermaid).

## Notes

- Thresholds default: running 5% (1:20), cross ~2.083% (1:48).
- For rasterio/GDAL on Lambda: current wheels may suffice. If not, re-base Docker image on a GDAL-bundled base in a follow-up PR.

