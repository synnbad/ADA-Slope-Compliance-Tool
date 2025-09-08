terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

resource "aws_s3_bucket" "site" {
  bucket = var.bucket_name
  tags = {
    Project    = "ADA"
    Env        = var.stage
    Owner      = "synnbad"
    CostCenter = "demo"
  }
}

resource "aws_s3_bucket_website_configuration" "site" {
  bucket = aws_s3_bucket.site.id
  index_document {
    suffix = "index.html"
  }
}

resource "aws_s3_bucket_public_access_block" "site" {
  bucket = aws_s3_bucket.site.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}

resource "aws_s3_bucket_policy" "site" {
  bucket = aws_s3_bucket.site.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Sid       = "PublicReadGetObject",
        Effect    = "Allow",
        Principal = "*",
        Action    = ["s3:GetObject"],
        Resource  = ["${aws_s3_bucket.site.arn}/*"]
      }
    ]
  })
}

resource "aws_ecr_repository" "api" {
  name                 = "${var.project}-api"
  image_tag_mutability = "MUTABLE"
  force_delete         = true
  tags = {
    Project    = "ADA"
    Env        = var.stage
    Owner      = "synnbad"
    CostCenter = "demo"
  }
}

resource "aws_apigatewayv2_api" "http" {
  name          = "${var.project}-http"
  protocol_type = "HTTP"
  cors_configuration = {
    allow_headers = ["content-type"]
    allow_methods = ["GET", "POST", "OPTIONS"]
    allow_origins = var.s3_site_origin != "" ? [var.s3_site_origin] : ["*"]
    max_age       = 600
  }
  tags = {
    Project    = "ADA"
    Env        = var.stage
    Owner      = "synnbad"
    CostCenter = "demo"
  }
}

resource "aws_lambda_function" "api" {
  function_name = "${var.project}-api"
  package_type  = "Image"
  image_uri     = var.lambda_image_uri
  timeout       = 60
  memory_size   = 1024
  environment {
    variables = {
      STAGE = var.stage
    }
  }
  tags = {
    Project    = "ADA"
    Env        = var.stage
    Owner      = "synnbad"
    CostCenter = "demo"
  }
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_method     = "POST"
  integration_uri        = aws_lambda_function.api.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.http.id
  route_key = "$default"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_cloudwatch_log_group" "lambda" {
  name              = "/aws/lambda/${aws_lambda_function.api.function_name}"
  retention_in_days = 7
  tags = {
    Project    = "ADA"
    Env        = var.stage
    Owner      = "synnbad"
    CostCenter = "demo"
  }
}
