#!/usr/bin/env python
"""
Script to check AWS configuration for the Intelligent LLM Agent project.
"""

import os
import sys
import boto3
import json
from botocore.exceptions import ClientError, NoCredentialsError


def check_aws_credentials():
    """Check if AWS credentials are configured."""
    try:
        # Create a boto3 session
        session = boto3.Session()
        
        # Get the credentials
        credentials = session.get_credentials()
        
        if credentials is None:
            print("❌ AWS credentials not found.")
            print("   Please configure AWS credentials using AWS CLI:")
            print("   aws configure")
            return False
        
        # Get the caller identity to verify credentials
        sts = session.client('sts')
        identity = sts.get_caller_identity()
        
        print(f"✅ AWS credentials found.")
        print(f"   Account: {identity['Account']}")
        print(f"   User: {identity['Arn']}")
        return True
    
    except NoCredentialsError:
        print("❌ AWS credentials not found.")
        print("   Please configure AWS credentials using AWS CLI:")
        print("   aws configure")
        return False
    
    except ClientError as e:
        print(f"❌ Error checking AWS credentials: {e}")
        return False


def check_aws_region():
    """Check if AWS region is configured."""
    try:
        # Create a boto3 session
        session = boto3.Session()
        
        # Get the region
        region = session.region_name
        
        if region is None:
            print("❌ AWS region not configured.")
            print("   Please configure AWS region using AWS CLI:")
            print("   aws configure")
            return False
        
        print(f"✅ AWS region configured: {region}")
        return True
    
    except Exception as e:
        print(f"❌ Error checking AWS region: {e}")
        return False


def check_lambda_permissions():
    """Check if the user has permissions to create Lambda functions."""
    try:
        # Create a boto3 session
        session = boto3.Session()
        
        # Create a Lambda client
        lambda_client = session.client('lambda')
        
        # List Lambda functions to check permissions
        lambda_client.list_functions(MaxItems=1)
        
        print("✅ Lambda permissions verified.")
        return True
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("❌ No permissions to access Lambda.")
            print("   Please ensure your AWS user has the necessary permissions.")
            return False
        else:
            print(f"❌ Error checking Lambda permissions: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error checking Lambda permissions: {e}")
        return False


def check_dynamodb_permissions():
    """Check if the user has permissions to create DynamoDB tables."""
    try:
        # Create a boto3 session
        session = boto3.Session()
        
        # Create a DynamoDB client
        dynamodb_client = session.client('dynamodb')
        
        # List DynamoDB tables to check permissions
        dynamodb_client.list_tables(Limit=1)
        
        print("✅ DynamoDB permissions verified.")
        return True
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("❌ No permissions to access DynamoDB.")
            print("   Please ensure your AWS user has the necessary permissions.")
            return False
        else:
            print(f"❌ Error checking DynamoDB permissions: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error checking DynamoDB permissions: {e}")
        return False


def check_cloudwatch_permissions():
    """Check if the user has permissions to create CloudWatch logs."""
    try:
        # Create a boto3 session
        session = boto3.Session()
        
        # Create a CloudWatch client
        cloudwatch_client = session.client('logs')
        
        # List log groups to check permissions
        cloudwatch_client.describe_log_groups(limit=1)
        
        print("✅ CloudWatch permissions verified.")
        return True
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("❌ No permissions to access CloudWatch.")
            print("   Please ensure your AWS user has the necessary permissions.")
            return False
        else:
            print(f"❌ Error checking CloudWatch permissions: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Error checking CloudWatch permissions: {e}")
        return False


def check_terraform_installed():
    """Check if Terraform is installed."""
    try:
        import subprocess
        
        # Run terraform version command
        result = subprocess.run(['terraform', '--version'], capture_output=True, text=True)
        
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ Terraform installed: {version}")
            return True
        else:
            print("❌ Terraform not installed or not in PATH.")
            print("   Please install Terraform: https://www.terraform.io/downloads.html")
            return False
    
    except FileNotFoundError:
        print("❌ Terraform not installed or not in PATH.")
        print("   Please install Terraform: https://www.terraform.io/downloads.html")
        return False
    
    except Exception as e:
        print(f"❌ Error checking Terraform installation: {e}")
        return False


def main():
    """Main function."""
    print("=== AWS Configuration Check ===")
    
    # Check AWS credentials
    credentials_ok = check_aws_credentials()
    
    if not credentials_ok:
        print("\n❌ AWS credentials check failed. Please configure AWS credentials.")
        return
    
    # Check AWS region
    region_ok = check_aws_region()
    
    if not region_ok:
        print("\n❌ AWS region check failed. Please configure AWS region.")
        return
    
    # Check permissions
    print("\n=== AWS Permissions Check ===")
    lambda_ok = check_lambda_permissions()
    dynamodb_ok = check_dynamodb_permissions()
    cloudwatch_ok = check_cloudwatch_permissions()
    
    # Check Terraform
    print("\n=== Terraform Check ===")
    terraform_ok = check_terraform_installed()
    
    # Summary
    print("\n=== Summary ===")
    if all([credentials_ok, region_ok, lambda_ok, dynamodb_ok, cloudwatch_ok, terraform_ok]):
        print("✅ All checks passed. You're ready to deploy the Intelligent LLM Agent!")
    else:
        print("❌ Some checks failed. Please fix the issues before deploying.")
    
    print("\n=== End of AWS Configuration Check ===")


if __name__ == "__main__":
    main()
