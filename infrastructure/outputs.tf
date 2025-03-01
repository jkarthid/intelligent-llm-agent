output "lambda_function_name" {
  description = "Name of the Lambda function"
  value       = module.lambda_function.function_name
}

output "lambda_function_arn" {
  description = "ARN of the Lambda function"
  value       = module.lambda_function.function_arn
}

output "lambda_function_url" {
  description = "URL of the Lambda function"
  value       = module.lambda_function.function_url
}

output "dynamodb_table_name" {
  description = "Name of the DynamoDB table for caching"
  value       = var.cache_type == "dynamodb" ? aws_dynamodb_table.cache_table[0].name : "Not using DynamoDB"
}

output "cloudwatch_dashboard_url" {
  description = "URL of the CloudWatch dashboard"
  value       = "https://${var.aws_region}.console.aws.amazon.com/cloudwatch/home?region=${var.aws_region}#dashboards:name=${aws_cloudwatch_dashboard.main.dashboard_name}"
}
