locals {
  # Determine if source_path is a directory or a file
  source_is_dir = try(dirname(var.source_path) != var.source_path, false)
  
  # If source_path is a directory, create a zip file from it
  # If source_path is a file, use it as the source
  source_path = local.source_is_dir ? var.source_path : dirname(var.source_path)
  source_file = local.source_is_dir ? null : basename(var.source_path)
}

# Create a zip file of the Lambda function code
data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = local.source_path
  output_path = "${path.module}/lambda_function.zip"
  excludes    = var.exclude_files
}

# Create the Lambda function
resource "aws_lambda_function" "this" {
  function_name    = var.function_name
  description      = var.description
  handler          = var.handler
  runtime          = var.runtime
  timeout          = var.timeout
  memory_size      = var.memory_size
  
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  
  role             = var.role_arn
  
  environment {
    variables = var.environment_variables
  }
  
  dynamic "vpc_config" {
    for_each = var.vpc_config != null ? [var.vpc_config] : []
    content {
      subnet_ids         = vpc_config.value.subnet_ids
      security_group_ids = vpc_config.value.security_group_ids
    }
  }
  
  tags = var.tags
}

# Create a Lambda function URL if requested
resource "aws_lambda_function_url" "this" {
  count = var.create_function_url ? 1 : 0
  
  function_name      = aws_lambda_function.this.function_name
  authorization_type = var.function_url_authorization_type
  
  cors {
    allow_credentials = var.cors_allow_credentials
    allow_origins     = var.cors_allow_origins
    allow_methods     = var.cors_allow_methods
    allow_headers     = var.cors_allow_headers
    expose_headers    = var.cors_expose_headers
    max_age           = var.cors_max_age
  }
}
