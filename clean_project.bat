@echo off
echo Cleaning up Intelligent LLM Agent project...
echo.

echo Removing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
for /r . %%f in (*.pyc) do @if exist "%%f" del "%%f"
for /r . %%f in (*.pyo) do @if exist "%%f" del "%%f"
for /r . %%f in (*.pyd) do @if exist "%%f" del "%%f"

echo Removing test cache files...
if exist .pytest_cache rd /s /q .pytest_cache
if exist .coverage del .coverage
if exist htmlcov rd /s /q htmlcov

echo Removing build files...
if exist build rd /s /q build
if exist dist rd /s /q dist
if exist *.egg-info rd /s /q *.egg-info

echo Removing Terraform cache files...
if exist infrastructure\.terraform rd /s /q infrastructure\.terraform
if exist infrastructure\.terraform.lock.hcl del infrastructure\.terraform.lock.hcl
if exist infrastructure\terraform.tfstate del infrastructure\terraform.tfstate
if exist infrastructure\terraform.tfstate.backup del infrastructure\terraform.tfstate.backup

echo.
echo Cleanup complete!

echo.
echo To remove the virtual environment, run: rd /s /q venv
