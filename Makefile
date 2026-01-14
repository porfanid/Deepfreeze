.PHONY: help install install-dev test lint format clean run-demo

help:
	@echo "Deep Freeze - Development Commands"
	@echo "==================================="
	@echo "make install       - Install package"
	@echo "make install-dev   - Install package with dev dependencies"
	@echo "make test          - Run tests with coverage"
	@echo "make lint          - Run linters (flake8, mypy)"
	@echo "make format        - Format code with Black"
	@echo "make clean         - Remove build artifacts and cache"
	@echo "make run-demo      - Run example demo"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

test:
	pytest --cov=deepfreeze --cov-report=html --cov-report=term

lint:
	flake8 src tests --max-line-length=88 --extend-ignore=E203,W503
	mypy src --ignore-missing-imports

format:
	black src tests

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run-demo:
	python examples/demo.py
