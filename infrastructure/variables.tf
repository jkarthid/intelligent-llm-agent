variable "aws_region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Name of the project"
  type        = string
  default     = "intelligent-llm-agent"
}

variable "llm_provider" {
  description = "LLM provider (openai, anthropic, bedrock, groq)"
  type        = string
  default     = "openai"
}

variable "llm_model" {
  description = "LLM model to use"
  type        = string
  default     = "gpt-4"
}

variable "use_cache" {
  description = "Whether to use caching"
  type        = bool
  default     = true
}

variable "cache_type" {
  description = "Type of cache to use (memory, dynamodb)"
  type        = string
  default     = "dynamodb"
}

variable "cache_ttl" {
  description = "TTL for cache items in seconds"
  type        = number
  default     = 86400  # 24 hours
}
