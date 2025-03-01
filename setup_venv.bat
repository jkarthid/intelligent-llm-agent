@echo off
echo Setting up Python virtual environment for Intelligent LLM Agent...
echo.

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH. Please install Python 3.9 or higher.
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
) else (
    echo Virtual environment already exists.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pytest pytest-cov flake8 black isort

REM Create .env file if it doesn't exist
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo Created .env file. Please update it with your configuration.
) else (
    echo .env file already exists.
)

echo.
echo Virtual environment setup complete!
echo.
echo To activate the virtual environment, run: venv\Scripts\activate.bat
echo To deactivate the virtual environment, run: deactivate
echo.
echo To run tests, activate the virtual environment and run: python -m pytest
echo To run linting checks, activate the virtual environment and run: python -m flake8 src/ tests/
echo To format code, activate the virtual environment and run: python -m black src/ tests/
echo.
echo To run the application locally, activate the virtual environment and run: python run_local.py
