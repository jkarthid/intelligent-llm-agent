.PHONY: setup test lint format clean deploy-dev deploy-prod

# Variables
PYTHON = python
PIP = pip
PYTEST = pytest
FLAKE8 = flake8
BLACK = black
ISORT = isort
TERRAFORM = terraform

# Setup development environment
setup:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .
	$(PIP) install pytest pytest-cov flake8 black isort

# Run tests
test:
	$(PYTEST) --cov=src tests/

# Run linting
lint:
	$(FLAKE8) src/ tests/
	$(BLACK) --check src/ tests/
	$(ISORT) --check-only src/ tests/

# Format code
format:
	$(BLACK) src/ tests/
	$(ISORT) src/ tests/

# Clean up build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Deploy to dev environment
deploy-dev:
	cd infrastructure && \
	$(TERRAFORM) init \
		-backend-config="bucket=your-terraform-state-bucket" \
		-backend-config="key=intelligent-llm-agent/dev/terraform.tfstate" \
		-backend-config="region=us-east-1" \
		-backend-config="dynamodb_table=terraform-state-lock" && \
	$(TERRAFORM) plan -var="environment=dev" -out=tfplan && \
	$(TERRAFORM) apply -auto-approve tfplan

# Deploy to production environment
deploy-prod:
	cd infrastructure && \
	$(TERRAFORM) init \
		-backend-config="bucket=your-terraform-state-bucket" \
		-backend-config="key=intelligent-llm-agent/prod/terraform.tfstate" \
		-backend-config="region=us-east-1" \
		-backend-config="dynamodb_table=terraform-state-lock" && \
	$(TERRAFORM) plan -var="environment=prod" -out=tfplan && \
	$(TERRAFORM) apply -auto-approve tfplan

# Run locally
run-local:
	$(PYTHON) -m src.aws.lambda_handler

# Help
help:
	@echo "Available commands:"
	@echo "  setup       - Install dependencies and set up development environment"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black and isort"
	@echo "  clean       - Clean up build artifacts"
	@echo "  deploy-dev  - Deploy to dev environment"
	@echo "  deploy-prod - Deploy to production environment"
	@echo "  run-local   - Run the application locally"
