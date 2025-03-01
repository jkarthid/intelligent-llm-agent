@echo off
echo Deploying Intelligent LLM Agent from virtual environment...
echo.

REM Check if virtual environment exists
if not exist venv (
    echo Virtual environment not found. Please run setup_venv.bat first.
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Run tests before deployment
echo.
echo Running tests before deployment...
python -m pytest || (
    echo Tests failed. Deployment aborted.
    call deactivate
    exit /b 1
)

REM Check if Terraform is installed
terraform --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Terraform is not installed or not in PATH. Please install Terraform.
    call deactivate
    exit /b 1
)

REM Deploy to AWS using Terraform
echo.
echo Deploying to AWS using Terraform...
cd infrastructure
terraform init
terraform validate || (
    echo Terraform validation failed. Deployment aborted.
    cd ..
    call deactivate
    exit /b 1
)

echo.
echo Ready to apply Terraform changes.
echo This will deploy resources to AWS. Make sure you have the correct AWS credentials configured.
echo.
set /p CONFIRM=Do you want to continue? (y/n): 

if /i "%CONFIRM%" NEQ "y" (
    echo Deployment aborted by user.
    cd ..
    call deactivate
    exit /b 0
)

terraform apply || (
    echo Terraform apply failed. Deployment aborted.
    cd ..
    call deactivate
    exit /b 1
)

cd ..

echo.
echo Deployment completed successfully!

REM Deactivate virtual environment
call deactivate
