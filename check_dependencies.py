#!/usr/bin/env python
"""
Script to check the installed dependencies and their versions.
"""

import importlib
import importlib.metadata
import sys


def get_package_version(package_name):
    """Get the version of an installed package."""
    try:
        return importlib.metadata.version(package_name)
    except importlib.metadata.PackageNotFoundError:
        return "Not installed"


def main():
    """Main function."""
    print("=== Dependency Check ===")
    print(f"Python version: {sys.version}")
    
    # List of packages to check
    packages = [
        "boto3",
        "pydantic",
        "python-dotenv",
        "pytest",
        "pytest-mock",
        "requests",
        "aws-lambda-powertools",
        "openai",
        "groq",
        "anthropic",
        "black",
        "flake8",
        "isort"
    ]
    
    # Check each package
    for package in packages:
        version = get_package_version(package)
        print(f"{package}: {version}")
    
    print("\n=== Dependency Check Complete ===")


if __name__ == "__main__":
    main()
