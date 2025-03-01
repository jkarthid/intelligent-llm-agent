# Contributing to Intelligent LLM Agent

Thank you for considering contributing to the Intelligent LLM Agent project! This document outlines the process for contributing to the project.

## Code of Conduct

By participating in this project, you are expected to uphold our Code of Conduct, which is to be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with the following information:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Any relevant logs or screenshots

### Suggesting Enhancements

If you have an idea for an enhancement, please create an issue on GitHub with the following information:

- A clear, descriptive title
- A detailed description of the enhancement
- Any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature or bug fix
3. Make your changes
4. Run the tests to ensure your changes don't break existing functionality
5. Submit a pull request

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/yourusername/intelligent-llm-agent.git
cd intelligent-llm-agent/intelligent-llm-agent-aws
```

2. Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
pip install pytest pytest-cov flake8 black isort
```

3. Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

4. Edit the `.env` file with your configuration.

## Running Tests

```bash
pytest --cov=src tests/
```

## Coding Standards

- Follow PEP 8 style guide
- Use type hints
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused
- Write unit tests for all new functionality

## Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.
