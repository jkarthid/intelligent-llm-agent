@echo off
echo Generating project report for Intelligent LLM Agent...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the report generation script
echo.
echo Running report generation...
python generate_report.py

REM Deactivate virtual environment
call deactivate
