terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    # These values need to be provided via terraform init -backend-config
    # bucket         = "your-terraform-state-bucket"
    # key            = "intelligent-llm-agent/terraform.tfstate"
    # region         = "us-east-1"
    # dynamodb_table = "terraform-state-lock"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "IntelligentLLMAgent"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Random ID for unique resource naming
resource "random_id" "id" {
  byte_length = 8
}

# Create a Lambda function for the agent
module "lambda_function" {
  source = "./modules/lambda"
  
  function_name        = "${var.project_name}-${var.environment}"
  description          = "Intelligent LLM Agent with Dynamic Tool Selection and Caching"
  handler              = "src.aws.lambda_handler.lambda_handler"
  runtime              = "python3.9"
  timeout              = 300
  memory_size          = 512
  
  source_path          = "${path.module}/../"
  exclude_files        = ["infrastructure/", "ci-cd/", "tests/", ".git/"]
  
  environment_variables = {
    LLM_PROVIDER    = var.llm_provider
    LLM_MODEL       = var.llm_model
    USE_CACHE       = var.use_cache
    CACHE_TYPE      = var.cache_type
    DYNAMODB_TABLE  = var.cache_type == "dynamodb" ? aws_dynamodb_table.cache_table[0].name : ""
    LOG_LEVEL       = "INFO"
  }
  
  create_function_url = true
  function_url_authorization_type = "NONE" # For simplicity, change to "AWS_IAM" for production
  
  depends_on = [
    aws_dynamodb_table.cache_table
  ]
}

# Create a DynamoDB table for caching if cache_type is dynamodb
resource "aws_dynamodb_table" "cache_table" {
  count = var.cache_type == "dynamodb" ? 1 : 0
  
  name           = "${var.project_name}-cache-${var.environment}"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "cache_key"
  
  attribute {
    name = "cache_key"
    type = "S"
  }
  
  attribute {
    name = "feedback_id"
    type = "S"
  }
  
  global_secondary_index {
    name               = "FeedbackIdIndex"
    hash_key           = "feedback_id"
    projection_type    = "ALL"
    write_capacity     = 0
    read_capacity      = 0
  }
  
  ttl {
    attribute_name = "expiry"
    enabled        = true
  }
  
  point_in_time_recovery {
    enabled = true
  }
  
  tags = {
    Name = "${var.project_name}-cache-${var.environment}"
  }
}

# Create CloudWatch Log Group for Lambda
resource "aws_cloudwatch_log_group" "lambda_log_group" {
  name              = "/aws/lambda/${module.lambda_function.function_name}"
  retention_in_days = 30
}

# Create CloudWatch Dashboard for monitoring
resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "${var.project_name}-dashboard-${var.environment}"
  
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["AWS/Lambda", "Invocations", "FunctionName", module.lambda_function.function_name],
            ["AWS/Lambda", "Errors", "FunctionName", module.lambda_function.function_name],
            ["AWS/Lambda", "Duration", "FunctionName", module.lambda_function.function_name]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Lambda Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            ["IntelligentLLMAgent", "CacheHits", "MetricType", "Cache"],
            ["IntelligentLLMAgent", "CacheMisses", "MetricType", "Cache"],
            ["IntelligentLLMAgent", "CacheHitRatio", "MetricType", "Cache"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Cache Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 24
        height = 6
        properties = {
          metrics = [
            ["IntelligentLLMAgent", "ToolExecutionTime", "ToolName", "sentiment_analysis"],
            ["IntelligentLLMAgent", "ToolExecutionTime", "ToolName", "topic_categorization"],
            ["IntelligentLLMAgent", "ToolExecutionTime", "ToolName", "keyword_contextualization"],
            ["IntelligentLLMAgent", "ToolExecutionTime", "ToolName", "summarization"]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Tool Execution Time"
          period  = 300
        }
      }
    ]
  })
}

# Create IAM role for the Lambda function
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role-${var.environment}"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach policies to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Create a policy for DynamoDB access if cache_type is dynamodb
resource "aws_iam_policy" "dynamodb_policy" {
  count = var.cache_type == "dynamodb" ? 1 : 0
  
  name        = "${var.project_name}-dynamodb-policy-${var.environment}"
  description = "Policy for DynamoDB access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan",
          "dynamodb:BatchWriteItem"
        ]
        Effect   = "Allow"
        Resource = aws_dynamodb_table.cache_table[0].arn
      }
    ]
  })
}

# Attach the DynamoDB policy to the Lambda role if cache_type is dynamodb
resource "aws_iam_role_policy_attachment" "lambda_dynamodb" {
  count = var.cache_type == "dynamodb" ? 1 : 0
  
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.dynamodb_policy[0].arn
}

# Create a policy for CloudWatch Logs access
resource "aws_iam_policy" "cloudwatch_policy" {
  name        = "${var.project_name}-cloudwatch-policy-${var.environment}"
  description = "Policy for CloudWatch Logs access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents",
          "logs:DescribeLogStreams"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach the CloudWatch policy to the Lambda role
resource "aws_iam_role_policy_attachment" "lambda_cloudwatch" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.cloudwatch_policy.arn
}

# Create a policy for Bedrock access if llm_provider is bedrock
resource "aws_iam_policy" "bedrock_policy" {
  count = var.llm_provider == "bedrock" ? 1 : 0
  
  name        = "${var.project_name}-bedrock-policy-${var.environment}"
  description = "Policy for Bedrock access"
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "bedrock:InvokeModel"
        ]
        Effect   = "Allow"
        Resource = "*"
      }
    ]
  })
}

# Attach the Bedrock policy to the Lambda role if llm_provider is bedrock
resource "aws_iam_role_policy_attachment" "lambda_bedrock" {
  count = var.llm_provider == "bedrock" ? 1 : 0
  
  role       = aws_iam_role.lambda_role.name
  policy_arn = aws_iam_policy.bedrock_policy[0].arn
}
