@echo off
echo Checking project structure for Intelligent LLM Agent...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the project structure check script
echo.
echo Running project structure check...
python check_structure.py

REM Deactivate virtual environment
call deactivate
