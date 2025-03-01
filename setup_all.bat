@echo off
echo Setting up everything for Intelligent LLM Agent...
echo.

REM Setup virtual environment
echo Setting up virtual environment...
call setup_venv.bat

REM Check project structure
echo.
echo Checking project structure...
call check_structure.bat

REM Check AWS configuration
echo.
echo Checking AWS configuration...
call check_aws.bat

REM Run tests
echo.
echo Running tests...
call run_all_tests.bat

REM Generate report
echo.
echo Generating project report...
call run_report.bat

echo.
echo All setup complete!
echo.
echo The following scripts are available:
echo - setup_venv.bat: Set up the virtual environment
echo - check_structure.bat: Check project structure
echo - check_aws.bat: Check AWS configuration
echo - run_all_tests.bat: Run all tests
echo - run_tests.bat: Run unit tests
echo - run_lint.bat: Run linting checks
echo - format_code.bat: Format the code
echo - run_app.bat: Run the application locally
echo - run_in_venv.bat: Run the application in the virtual environment
echo - deploy_from_venv.bat: Deploy to AWS
echo - update_docs.bat: Update documentation
echo - run_report.bat: Generate project report
echo - clean_project.bat: Clean up the project
echo - create_release.bat: Create a new release
echo.
echo To get started, run: run_in_venv.bat
