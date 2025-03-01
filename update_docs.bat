@echo off
echo Updating documentation for Intelligent LLM Agent...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Generate project report
echo.
echo Generating project report...
python generate_report.py

REM Update README.md with latest information
echo.
echo Updating README.md with latest information...
echo.
echo This step requires manual review. Please update the README.md file with the latest information.
echo The project report has been generated and can be used to update the README.md file.
echo.
echo Press any key to open README.md in your default editor...
pause > nul
start README.md

REM Update other documentation files
echo.
echo Updating other documentation files...
echo.
echo This step requires manual review. Please update the following documentation files with the latest information:
echo - docs/api.md
echo - docs/architecture.md
echo - docs/usage.md
echo - docs/project_summary.md
echo - docs/project_status.md
echo.
echo Press any key to open the docs directory...
pause > nul
start docs

REM Deactivate virtual environment
call deactivate
