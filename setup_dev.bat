@echo off
echo Setting up development environment for Intelligent LLM Agent...
echo.
echo Installing dependencies...
pip install -r requirements.txt
pip install -e .
pip install pytest pytest-cov flake8 black isort
echo.
echo Creating .env file if it doesn't exist...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example. Please update it with your configuration.
) else (
    echo .env file already exists.
)
echo.
echo Development environment setup complete!
