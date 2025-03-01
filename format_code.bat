@echo off
echo Formatting code for Intelligent LLM Agent...
echo.
echo Running black...
python -m black src/ tests/
echo.
echo Running isort...
python -m isort src/ tests/
echo.
echo Code formatting complete!
