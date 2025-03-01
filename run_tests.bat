@echo off
echo Running tests for Intelligent LLM Agent...
python -m pytest --cov=src tests/ -v
echo.
echo Test run complete!
