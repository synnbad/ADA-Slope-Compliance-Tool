variable "project" { type = string  default = "ada-slope" }
variable "region"  { type = string  default = "us-east-1" }
variable "stage"   { type = string  default = "dev" }
variable "bucket_name" { type = string }
variable "lambda_image_uri" { type = string } # e.g., ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/ada-slope-api:latest
