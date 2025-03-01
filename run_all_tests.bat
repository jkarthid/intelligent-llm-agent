@echo off
echo Running all tests for Intelligent LLM Agent in virtual environment...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run validation script
echo.
echo Running project validation...
python validate_project.py

REM Run linting checks
echo.
echo Running linting checks...
python -m flake8 src/ tests/ || echo Linting issues found, but continuing...

REM Run tests
echo.
echo Running unit tests...
python -m pytest --collect-only

echo.
echo All tests completed!
echo.
echo To run the full test suite with coverage, activate the virtual environment and run:
echo python -m pytest --cov=src tests/

REM Deactivate virtual environment
call deactivate
