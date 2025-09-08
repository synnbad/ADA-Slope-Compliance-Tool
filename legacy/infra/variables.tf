variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name prefix"
  type        = string
  default     = "ada-slope"
}

variable "stage" {
  description = "Deployment stage"
  type        = string
  default     = "dev"
}

variable "bucket_name" {
  description = "S3 bucket for website hosting (must be globally unique)"
  type        = string
}

variable "lambda_image_uri" {
  description = "ECR image URI for Lambda container"
  type        = string
}

variable "s3_site_origin" {
  description = "Origin URL for CORS (e.g., https://bucket.s3-website-us-east-1.amazonaws.com)"
  type        = string
  default     = ""
}

variable "project" { type = string  default = "ada-slope" }
variable "region"  { type = string  default = "us-east-1" }
variable "stage"   { type = string  default = "dev" }
variable "bucket_name" { type = string }
variable "lambda_image_uri" { type = string } # e.g., ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ada-slope-api:latest
