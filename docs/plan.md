# ADA Slope Compliance Tool — AWS MVP Shipping Plan

Owner: Sinbad Adjuik
Repo: https://github.com/synnbad/ADA-Slope-Compliance-Tool

Objective: Ship a minimal, credible, low-cost AWS-hosted demo with a FastAPI Lambda container + API Gateway, with a static S3 frontend. Start with an audit and core-logic improvements, then infrastructure and CI/CD.

## Scope (MVP)
- Audit & improvements (pre-AWS)
- Backend API: POST /upload, GET /status/{job_id}, GET /results/{job_id}
- Slope engine: NumPy gradients; thresholds param (running 5%, cross ~2.083%)
- Tests: processing + API; synthetic data; coverage target ~80% processing
- Infra: Terraform for ECR, Lambda (Image), API GW (HTTP), DynamoDB (stub), S3
- CI/CD: Python checks; ECR build on tag; TF plan on PR
- Docs: README, architecture diagram (Mermaid), demo data provenance

## Risks
Rasterio/GDAL on Lambda (consider GDAL-bundled base if needed), timeouts/file size, CORS/config drift, costs, data licensing.

## Next iterations
DynamoDB+S3 persistence, richer UI, CloudFront, auth/quotas, async pipeline, expanded ADA logic.
