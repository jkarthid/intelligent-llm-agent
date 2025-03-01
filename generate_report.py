#!/usr/bin/env python
"""
Script to generate a project report for the Intelligent LLM Agent.
This includes code statistics, test coverage, and documentation status.
"""

import os
import subprocess
import datetime
import json
from pathlib import Path


def count_lines(directory, file_extension):
    """Count the number of lines in files with the given extension."""
    total_lines = 0
    file_count = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(file_extension):
                file_path = os.path.join(root, file)
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                    total_lines += len(lines)
                    file_count += 1
    
    return total_lines, file_count


def run_command(command):
    """Run a command and return the output."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {command}")
        print(f"Error message: {e.stderr}")
        return ""


def get_test_coverage():
    """Get the test coverage percentage."""
    coverage_output = run_command("python -m pytest --cov=src tests/ --cov-report=term-missing")
    
    # Extract coverage percentage
    for line in coverage_output.split('\n'):
        if "TOTAL" in line:
            parts = line.split()
            if len(parts) >= 4:
                return parts[3]
    
    return "Unknown"


def get_documentation_status():
    """Get the documentation status."""
    docs_dir = Path("docs")
    docs_files = list(docs_dir.glob("*.md"))
    
    return {
        "total_docs": len(docs_files),
        "docs_files": [f.name for f in docs_files]
    }


def get_git_info():
    """Get information from git."""
    last_commit = run_command("git log -1 --pretty=format:'%h - %s (%an, %ad)'")
    branch = run_command("git rev-parse --abbrev-ref HEAD").strip()
    
    return {
        "last_commit": last_commit.strip("'"),
        "branch": branch
    }


def generate_report():
    """Generate the project report."""
    report = {
        "project_name": "Intelligent LLM Agent",
        "report_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "code_statistics": {},
        "test_statistics": {},
        "documentation_status": {},
        "git_info": {}
    }
    
    # Code statistics
    python_lines, python_files = count_lines("src", ".py")
    test_lines, test_files = count_lines("tests", ".py")
    
    report["code_statistics"] = {
        "python_lines": python_lines,
        "python_files": python_files,
        "test_lines": test_lines,
        "test_files": test_files,
        "total_lines": python_lines + test_lines,
        "total_files": python_files + test_files
    }
    
    # Test statistics
    try:
        report["test_statistics"] = {
            "coverage": get_test_coverage()
        }
    except Exception as e:
        report["test_statistics"] = {
            "coverage": "Error getting coverage",
            "error": str(e)
        }
    
    # Documentation status
    report["documentation_status"] = get_documentation_status()
    
    # Git info
    try:
        report["git_info"] = get_git_info()
    except Exception as e:
        report["git_info"] = {
            "error": str(e)
        }
    
    return report


def save_report(report, output_file="project_report.json"):
    """Save the report to a file."""
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"Report saved to {output_file}")


def print_report(report):
    """Print the report to the console."""
    print("=" * 50)
    print(f"Project Report: {report['project_name']}")
    print(f"Date: {report['report_date']}")
    print("=" * 50)
    
    print("\nCode Statistics:")
    print(f"  Python Files: {report['code_statistics']['python_files']}")
    print(f"  Python Lines: {report['code_statistics']['python_lines']}")
    print(f"  Test Files: {report['code_statistics']['test_files']}")
    print(f"  Test Lines: {report['code_statistics']['test_lines']}")
    print(f"  Total Files: {report['code_statistics']['total_files']}")
    print(f"  Total Lines: {report['code_statistics']['total_lines']}")
    
    print("\nTest Statistics:")
    print(f"  Coverage: {report['test_statistics'].get('coverage', 'Unknown')}")
    
    print("\nDocumentation Status:")
    print(f"  Total Docs: {report['documentation_status']['total_docs']}")
    print("  Docs Files:")
    for doc in report['documentation_status']['docs_files']:
        print(f"    - {doc}")
    
    if "last_commit" in report['git_info']:
        print("\nGit Info:")
        print(f"  Branch: {report['git_info'].get('branch', 'Unknown')}")
        print(f"  Last Commit: {report['git_info'].get('last_commit', 'Unknown')}")
    
    print("\n" + "=" * 50)


def main():
    """Main function."""
    print("Generating project report...")
    report = generate_report()
    save_report(report)
    print_report(report)


if __name__ == "__main__":
    main()
