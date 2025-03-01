variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "description" {
  description = "Description of the Lambda function"
  type        = string
  default     = ""
}

variable "handler" {
  description = "Handler for the Lambda function"
  type        = string
}

variable "runtime" {
  description = "Runtime for the Lambda function"
  type        = string
  default     = "python3.9"
}

variable "timeout" {
  description = "Timeout for the Lambda function in seconds"
  type        = number
  default     = 3
}

variable "memory_size" {
  description = "Memory size for the Lambda function in MB"
  type        = number
  default     = 128
}

variable "source_path" {
  description = "Path to the source code"
  type        = string
}

variable "exclude_files" {
  description = "List of files to exclude from the zip"
  type        = list(string)
  default     = []
}

variable "role_arn" {
  description = "ARN of the IAM role for the Lambda function"
  type        = string
  default     = null
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "vpc_config" {
  description = "VPC configuration for the Lambda function"
  type = object({
    subnet_ids         = list(string)
    security_group_ids = list(string)
  })
  default = null
}

variable "tags" {
  description = "Tags for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "create_function_url" {
  description = "Whether to create a function URL"
  type        = bool
  default     = false
}

variable "function_url_authorization_type" {
  description = "Authorization type for the function URL"
  type        = string
  default     = "NONE"
}

variable "cors_allow_credentials" {
  description = "Whether to allow credentials for CORS"
  type        = bool
  default     = false
}

variable "cors_allow_origins" {
  description = "Allowed origins for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allow_methods" {
  description = "Allowed methods for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_allow_headers" {
  description = "Allowed headers for CORS"
  type        = list(string)
  default     = ["*"]
}

variable "cors_expose_headers" {
  description = "Exposed headers for CORS"
  type        = list(string)
  default     = []
}

variable "cors_max_age" {
  description = "Max age for CORS in seconds"
  type        = number
  default     = 0
}
