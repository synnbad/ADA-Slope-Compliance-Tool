ADA Slope Compliance — Minimal AWS Deploy Runbook

This guide walks you through building and deploying the minimal, low-cost stack:
- Backend: Lambda (container) + API Gateway (HTTP)
- Frontend: S3 website hosting a single HTML file
- No DynamoDB, CloudFront, queues, or provisioned concurrency

Assumptions:
- Region: us-east-1
- You have AWS CLI v2, Docker, and Terraform >= 1.5 installed and authenticated
- You’re okay with public-read for the S3 website

## 1) Build & Push the Lambda Image to ECR

Set variables up-front (change the bucket and optionally project/stage):

```bash
export REGION=us-east-1
export PROJECT=ada-slope
export STAGE=dev
export BUCKET=YOUR_UNIQUE_BUCKET_NAME # must be globally unique
```

Create ECR repo (idempotent) and push the image:

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REPO_URI=${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT}-api:latest

aws ecr create-repository --repository-name ${PROJECT}-api --region ${REGION} || true
aws ecr get-login-password --region ${REGION} \
  | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com

# Build from backend/ using the provided Dockerfile
docker build -t ${PROJECT}-api:latest -f backend/Dockerfile backend

docker tag ${PROJECT}-api:latest ${REPO_URI}
docker push ${REPO_URI}
```

## 2) Terraform Apply (S3 website + API Gateway + Lambda)

Initialize and apply:

```bash
cd infra
terraform init

# s3_site_origin is used to narrow API CORS to your website origin
# Format: http://<bucket>.s3-website-<region>.amazonaws.com
export SITE_ORIGIN=http://${BUCKET}.s3-website-${REGION}.amazonaws.com

terraform apply -auto-approve \
  -var="region=${REGION}" \
  -var="project=${PROJECT}" \
  -var="stage=${STAGE}" \
  -var="bucket_name=${BUCKET}" \
  -var="lambda_image_uri=${REPO_URI}" \
  -var="s3_site_origin=${SITE_ORIGIN}"
```

Outputs to note:
- `http_api_url`: your API Gateway base URL
- `s3_website_endpoint`: your website URL

CloudWatch Logs retention is set to 7 days. Tags applied: Project=ADA, Env=${STAGE}, Owner=synnbad, CostCenter=demo.

## 3) Set Frontend API URL and Upload to S3

Edit `frontend/index.html` and set the API base URL:

```js
const API_BASE = "https://<api-id>.execute-api.us-east-1.amazonaws.com";
```

Upload the file to the website bucket:

```bash
aws s3 cp ../frontend/index.html s3://${BUCKET}/index.html --acl public-read --region ${REGION}
```

Visit the S3 website endpoint from Terraform outputs and verify you can upload a small GeoTIFF and see JSON results.

## 4) Local Smoke Tests (Optional)

Run CI locally:

```bash
python -m pip install --upgrade pip
pip install -r backend/requirements.txt ruff pytest
ruff check .
PYTHONPATH=backend pytest -q
```

## 5) Manual Verification Checklist

- API
  - GET `${http_api_url}/healthz` returns `{ "status": "ok" }`
  - POST `${http_api_url}/upload` with a small `.tif` returns `{ job_id }`
  - GET `${http_api_url}/results/{job_id}` includes `summary` and `artifacts.histogram`
- Frontend
  - Website loads over `http://<bucket>.s3-website-...`
  - Uploading `.tif` shows parsed JSON with running and cross-slope metrics
- CORS
  - Browser network tab shows successful preflight and 200 responses

## 6) Guardrails & Limits (already enforced server-side)

- MIME check: `image/tiff` only and filename ends with `.tif`/`.tiff`
- Max upload: 25 MiB → returns 413
- Lambda: 1024 MB memory, 60s timeout
- Processing: nodata masked; running slope via `np.sqrt(gx**2 + gy**2)*100` and cross-slope via `abs(gy)*100` for axis=x (or `abs(gx)` for axis=y)

## 7) Costs

- S3: website static hosting + small storage → pennies
- API Gateway + Lambda: pay-per-request; light demo traffic safely <$5/month
- CloudWatch logs: 7-day retention to reduce idle costs

## 8) Troubleshooting

- 400 `ERR_BAD_MIME`: ensure file is `.tif`/`.tiff` and content-type is `image/tiff`
- 413 `ERR_SIZE_LIMIT`: file exceeds 25 MiB
- 500 `ERR_TIFF_READ`: invalid GeoTIFF; try exporting a simple single-band float32 DEM
- CORS errors: confirm `s3_site_origin` matches the website endpoint exactly; re-`terraform apply`
- Lambda image not found: verify `${REPO_URI}` and that the image was pushed to the same region

## 9) Rollback / Cleanup

To remove resources:

```bash
cd infra
terraform destroy -auto-approve \
  -var="region=${REGION}" \
  -var="project=${PROJECT}" \
  -var="stage=${STAGE}" \
  -var="bucket_name=${BUCKET}" \
  -var="lambda_image_uri=${REPO_URI}" \
  -var="s3_site_origin=${SITE_ORIGIN}"
```

Optionally delete the ECR repo:

```bash
aws ecr delete-repository --repository-name ${PROJECT}-api --force --region ${REGION}
```

## 10) Appendix — API Reference

- `GET /healthz` → `{ status, build }`
- `POST /upload` (multipart/form-data)
  - file: GeoTIFF (`image/tiff`, .tif/.tiff), <= 25 MiB
  - query params (optional): `running_slope_max=0.05`, `cross_slope_max=0.02083`, `assumed_path_axis=x|y`
  - returns: `{ job_id }`
- `GET /results/{id}` → `{ status: "done", summary: { … }, artifacts: { histogram: [10 bins] } }`

Summary keys:
- running_slope_threshold_pct, cross_slope_threshold_pct
- pixels_total
- pixels_violating_running, percent_violating_running
- pixels_violating_cross, percent_violating_cross
- max_slope_pct, mean_slope_pct
- pass_running, pass_cross


