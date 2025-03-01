#!/usr/bin/env python
"""
Script to check the project structure of the Intelligent LLM Agent.
"""

import os
import sys
from pathlib import Path


def check_directory(directory, expected_subdirs=None, expected_files=None):
    """Check if a directory exists and contains expected subdirectories and files."""
    if not os.path.isdir(directory):
        print(f"❌ Directory not found: {directory}")
        return False
    
    print(f"✅ Directory found: {directory}")
    
    all_ok = True
    
    if expected_subdirs:
        for subdir in expected_subdirs:
            subdir_path = os.path.join(directory, subdir)
            if not os.path.isdir(subdir_path):
                print(f"  ❌ Subdirectory not found: {subdir}")
                all_ok = False
            else:
                print(f"  ✅ Subdirectory found: {subdir}")
    
    if expected_files:
        for file in expected_files:
            file_path = os.path.join(directory, file)
            if not os.path.isfile(file_path):
                print(f"  ❌ File not found: {file}")
                all_ok = False
            else:
                print(f"  ✅ File found: {file}")
    
    return all_ok


def main():
    """Main function."""
    print("=== Project Structure Check ===")
    
    # Check root directory
    root_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"Root directory: {root_dir}")
    
    # Expected root files
    expected_root_files = [
        "README.md",
        "requirements.txt",
        "setup.py",
        "pytest.ini",
        ".env.example",
        "Makefile",
        "run_local.py"
    ]
    
    # Expected root directories
    expected_root_dirs = [
        "src",
        "tests",
        "infrastructure",
        "ci-cd",
        "docs"
    ]
    
    # Check root directory
    root_ok = check_directory(root_dir, expected_root_dirs, expected_root_files)
    
    # Check src directory
    src_dir = os.path.join(root_dir, "src")
    expected_src_dirs = [
        "agents",
        "tools",
        "cache",
        "aws",
        "utils"
    ]
    src_ok = check_directory(src_dir, expected_src_dirs)
    
    # Check tests directory
    tests_dir = os.path.join(root_dir, "tests")
    expected_tests_dirs = [
        "test_agents",
        "test_tools",
        "test_cache",
        "test_aws",
        "test_utils"
    ]
    tests_ok = check_directory(tests_dir, expected_tests_dirs)
    
    # Check infrastructure directory
    infra_dir = os.path.join(root_dir, "infrastructure")
    expected_infra_files = [
        "main.tf",
        "variables.tf",
        "outputs.tf"
    ]
    expected_infra_dirs = [
        "modules"
    ]
    infra_ok = check_directory(infra_dir, expected_infra_dirs, expected_infra_files)
    
    # Check docs directory
    docs_dir = os.path.join(root_dir, "docs")
    expected_docs_files = [
        "api.md",
        "architecture.md",
        "usage.md"
    ]
    docs_ok = check_directory(docs_dir, expected_files=expected_docs_files)
    
    # Check ci-cd directory
    cicd_dir = os.path.join(root_dir, "ci-cd")
    expected_cicd_files = [
        "github-actions-workflow.yml"
    ]
    cicd_ok = check_directory(cicd_dir, expected_files=expected_cicd_files)
    
    # Summary
    print("\n=== Summary ===")
    if all([root_ok, src_ok, tests_ok, infra_ok, docs_ok, cicd_ok]):
        print("✅ All structure checks passed.")
    else:
        print("❌ Some structure checks failed.")
    
    print("\n=== End of Project Structure Check ===")


if __name__ == "__main__":
    main()
