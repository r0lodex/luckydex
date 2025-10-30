.PHONY: help install install-dev clean test lint format run deploy-dev deploy-staging deploy-prod logs-dev logs-staging logs-prod

help:
	@echo "Available commands:"
	@echo "  make install       - Install production dependencies"
	@echo "  make install-dev   - Install development dependencies"
	@echo "  make clean         - Remove virtual environment and cache files"
	@echo "  make test          - Run tests with coverage"
	@echo "  make lint          - Run linting checks"
	@echo "  make format        - Format code with black"
	@echo "  make run           - Run the application locally"
	@echo "  make deploy-dev    - Deploy to development environment"
	@echo "  make deploy-staging- Deploy to staging environment"
	@echo "  make deploy-prod   - Deploy to production environment"
	@echo "  make logs-dev      - View development logs"
	@echo "  make logs-staging  - View staging logs"
	@echo "  make logs-prod     - View production logs"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf .coverage

test:
	pytest tests/ --cov=app --cov-report=html --cov-report=term

lint:
	flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 app.py --count --max-complexity=10 --max-line-length=127 --statistics

format:
	black app.py tests/

run:
	@if [ -f .env ]; then \
		echo "Loading environment variables from .env..."; \
		export $$(grep -v '^#' .env | xargs) && chalice local; \
	else \
		echo "No .env file found, running without environment variables..."; \
		chalice local; \
	fi

deploy-dev:
	chalice deploy --stage dev

deploy-staging:
	chalice deploy --stage staging

deploy-prod:
	@echo "⚠️  WARNING: You are about to deploy to PRODUCTION!"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		chalice deploy --stage prod; \
	else \
		echo "Deployment cancelled."; \
	fi

logs-dev:
	chalice logs --stage dev

logs-staging:
	chalice logs --stage staging

logs-prod:
	chalice logs --stage prod

