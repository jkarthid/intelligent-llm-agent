@echo off
echo Running Intelligent LLM Agent in virtual environment...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run the application
echo.
echo Running the application...
python run_local.py

REM Deactivate virtual environment
call deactivate
