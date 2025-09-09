.PHONY: help install test test-all quality security build docs clean format lint type-check
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	poetry install

test: ## Run tests for the current Python version
	poetry run pytest tests/ --cov=graphene_django_extras --cov-report=term-missing

test-all: ## Run tests for all Python/Django combinations
	poetry run tox

quality: ## Run code quality checks (black, isort, flake8, mypy)
	poetry run tox -e quality

security: ## Run security checks (bandit, pip-audit)
	poetry run tox -e security

build: ## Build the package
	poetry run tox -e build

docs: ## Build documentation with MkDocs
	poetry run tox -e docs

docs-serve: ## Build and serve documentation locally
	poetry run mkdocs serve

docs-build: ## Build documentation for production
	poetry run mkdocs build --clean

format: ## Format code with black and isort
	poetry run black .
	poetry run isort .

lint: ## Run linting checks
	poetry run flake8 .

type-check: ## Run type checking with mypy
	poetry run mypy graphene_django_extras

clean: ## Clean build artifacts and cache
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .tox/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Development shortcuts
dev-setup: install ## Set up development environment
	@echo "Development environment ready!"

dev-test: format lint type-check test ## Run development checks (format, lint, type-check, test)

# CI/CD shortcuts  
ci-quality: quality ## Run CI quality checks
ci-security: security ## Run CI security checks
ci-test: test-all ## Run CI tests
ci-build: build ## Run CI build

# Individual tox environments
tox-py310-django40: ## Run tests with Python 3.10 and Django 4.0
	poetry run tox -e py310-django40

tox-py310-django42: ## Run tests with Python 3.10 and Django 4.2
	poetry run tox -e py310-django42

tox-py310-django50: ## Run tests with Python 3.10 and Django 5.0
	poetry run tox -e py310-django50

tox-py310-django51: ## Run tests with Python 3.10 and Django 5.1
	poetry run tox -e py310-django51

tox-py311-django40: ## Run tests with Python 3.11 and Django 4.0
	poetry run tox -e py311-django40

tox-py311-django42: ## Run tests with Python 3.11 and Django 4.2
	poetry run tox -e py311-django42

tox-py311-django50: ## Run tests with Python 3.11 and Django 5.0
	poetry run tox -e py311-django50

tox-py311-django51: ## Run tests with Python 3.11 and Django 5.1
	poetry run tox -e py311-django51

tox-py312-django42: ## Run tests with Python 3.12 and Django 4.2
	poetry run tox -e py312-django42

tox-py312-django50: ## Run tests with Python 3.12 and Django 5.0
	poetry run tox -e py312-django50

tox-py312-django51: ## Run tests with Python 3.12 and Django 5.1
	poetry run tox -e py312-django51