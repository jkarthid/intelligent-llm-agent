@echo off
echo Checking AWS configuration for Intelligent LLM Agent...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the AWS configuration check script
echo.
echo Running AWS configuration check...
python check_aws_config.py

REM Deactivate virtual environment
call deactivate
