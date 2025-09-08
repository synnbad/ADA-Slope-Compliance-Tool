output "http_api_url" {
  value = aws_apigatewayv2_api.http.api_endpoint
}

output "s3_website_endpoint" {
  value = aws_s3_bucket_website_configuration.site.website_endpoint
}

output "http_api_url" {
  value = aws_apigatewayv2_api.http.api_endpoint
}