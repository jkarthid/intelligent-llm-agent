#!/usr/bin/env python
"""
Validation script for the Intelligent LLM Agent project.
This script checks the project structure, imports, and configuration.
"""

import importlib
import os
import sys
from pathlib import Path


def check_file_exists(file_path, required=True):
    """Check if a file exists."""
    exists = os.path.isfile(file_path)
    if required and not exists:
        print(f"❌ Required file not found: {file_path}")
        return False
    elif exists:
        print(f"✅ File found: {file_path}")
        return True
    else:
        print(f"⚠️ Optional file not found: {file_path}")
        return True


def check_directory_exists(dir_path, required=True):
    """Check if a directory exists."""
    exists = os.path.isdir(dir_path)
    if required and not exists:
        print(f"❌ Required directory not found: {dir_path}")
        return False
    elif exists:
        print(f"✅ Directory found: {dir_path}")
        return True
    else:
        print(f"⚠️ Optional directory not found: {dir_path}")
        return True


def check_module_imports(module_name):
    """Check if a module can be imported."""
    try:
        importlib.import_module(module_name)
        print(f"✅ Module can be imported: {module_name}")
        return True
    except ImportError as e:
        print(f"❌ Module import failed: {module_name} - {str(e)}")
        return False


def validate_project_structure():
    """Validate the project structure."""
    print("\n=== Validating Project Structure ===\n")
    
    # Check root directories
    root_dirs = ["src", "tests", "infrastructure", "ci-cd", "docs"]
    for dir_name in root_dirs:
        check_directory_exists(dir_name)
    
    # Check src subdirectories
    src_dirs = ["agents", "tools", "cache", "aws", "utils"]
    for dir_name in src_dirs:
        check_directory_exists(os.path.join("src", dir_name))
    
    # Check tests subdirectories
    test_dirs = ["test_agents", "test_tools", "test_cache", "test_aws", "test_utils"]
    for dir_name in test_dirs:
        check_directory_exists(os.path.join("tests", dir_name))
    
    # Check key files
    key_files = [
        "README.md",
        "requirements.txt",
        "setup.py",
        "pytest.ini",
        ".env.example",
        "Makefile",
        "run_local.py"
    ]
    for file_name in key_files:
        check_file_exists(file_name)
    
    # Check infrastructure files
    infra_files = [
        os.path.join("infrastructure", "main.tf"),
        os.path.join("infrastructure", "variables.tf"),
        os.path.join("infrastructure", "outputs.tf")
    ]
    for file_name in infra_files:
        check_file_exists(file_name)
    
    # Check CI/CD files
    cicd_files = [
        os.path.join("ci-cd", "github-actions-workflow.yml")
    ]
    for file_name in cicd_files:
        check_file_exists(file_name)


def validate_module_imports():
    """Validate module imports."""
    print("\n=== Validating Module Imports ===\n")
    
    # Check core modules
    core_modules = [
        "src.agents.agent_factory",
        "src.agents.interaction_agent",
        "src.agents.tool_agent",
        "src.tools.tool_factory",
        "src.tools.sentiment_analysis",
        "src.tools.topic_categorization",
        "src.tools.keyword_contextualization",
        "src.tools.summarization",
        "src.cache.cache_manager",
        "src.cache.dynamodb_cache",
        "src.aws.lambda_handler",
        "src.aws.cloudwatch_logger",
        "src.utils.input_validator",
        "src.utils.error_handler"
    ]
    
    for module_name in core_modules:
        check_module_imports(module_name)


def validate_dependencies():
    """Validate dependencies."""
    print("\n=== Validating Dependencies ===\n")
    
    # Check required packages
    required_packages = [
        "boto3",
        "pytest",
        "python-dotenv",
        "openai"
    ]
    
    for package_name in required_packages:
        try:
            importlib.import_module(package_name)
            print(f"✅ Package installed: {package_name}")
        except ImportError:
            print(f"❌ Package not installed: {package_name}")


def validate_environment():
    """Validate environment variables."""
    print("\n=== Validating Environment Variables ===\n")
    
    # Check if .env file exists
    if not os.path.isfile(".env"):
        print("⚠️ .env file not found. Using environment variables.")
    else:
        print("✅ .env file found.")
    
    # Check required environment variables
    required_env_vars = [
        "LLM_PROVIDER",
        "LLM_MODEL",
        "USE_CACHE",
        "CACHE_TYPE"
    ]
    
    for var_name in required_env_vars:
        if var_name in os.environ:
            print(f"✅ Environment variable set: {var_name}")
        else:
            print(f"⚠️ Environment variable not set: {var_name}")


def main():
    """Main function."""
    print("=== Intelligent LLM Agent Project Validation ===")
    print(f"Current directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Change to project root directory if not already there
    project_root = Path(__file__).parent
    os.chdir(project_root)
    
    # Run validation checks
    validate_project_structure()
    validate_module_imports()
    validate_dependencies()
    validate_environment()
    
    print("\n=== Validation Complete ===")


if __name__ == "__main__":
    main()
