.PHONY: help install test test-coverage lint format tf-init tf-fmt tf-validate tf-plan-dev docker-build docker-run-mock clean

PYTHON ?= python
PIP ?= pip
TERRAFORM ?= terraform
DOCKER ?= docker

help: ## Display this help screen
	@echo "Available Makefile Commands:"
	@echo "----------------------------"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies for Lambda and Simulator
	$(PIP) install --upgrade pip
	$(PIP) install -r lambda/requirements.txt
	$(PIP) install -r device-simulator/requirements.txt
	$(PIP) install flake8 black pytest pytest-cov

test: ## Run unit tests across all project modules
	pytest lambda/test_lambda_function.py device-simulator/test_publisher.py -v

test-coverage: ## Run unit tests and generate coverage report
	pytest --cov=lambda --cov=device-simulator lambda/test_lambda_function.py device-simulator/test_publisher.py -v --cov-report=term-missing

lint: ## Check code formatting and syntax style
	flake8 lambda/ device-simulator/ --count --max-line-length=127 --statistics
	black --check lambda/ device-simulator/

format: ## Format all Python code with Black
	black lambda/ device-simulator/

tf-init: ## Initialize Terraform providers
	$(TERRAFORM) -chdir=terraform init -backend=false

tf-fmt: ## Check formatting of Terraform manifests
	$(TERRAFORM) -chdir=terraform fmt -check

tf-validate: ## Validate Terraform syntax and configuration
	$(TERRAFORM) -chdir=terraform validate

tf-plan-dev: tf-init ## Run dry-run plan against development environment tfvars
	$(TERRAFORM) -chdir=terraform plan -var-file=environments/dev.tfvars

docker-build: ## Build the hardened container image for device simulator
	$(DOCKER) build -t iot-device-simulator:latest ./device-simulator

docker-run-mock: ## Run simulator container locally in offline mock mode
	$(DOCKER) run --rm -e MOCK_MODE=true -e MAX_ITERATIONS=5 iot-device-simulator:latest

clean: ## Clean cached python files, test artifacts, and build outputs
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -f terraform/lambda_function_payload.zip 2>/dev/null || true
