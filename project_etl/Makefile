.PHONY: help install test clean run lint format

help:
	@echo "ETL Pipeline - Available Commands"
	@echo "=================================="
	@echo "make install    - Install dependencies"
	@echo "make test       - Run tests"
	@echo "make run        - Run the pipeline"
	@echo "make clean      - Clean up generated files"
	@echo "make lint       - Run code linting"
	@echo "make format     - Format code with black"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src --cov-report=html

run:
	python -m src.pipeline

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -f logs/*.log
	rm -f data/processed/*.db

lint:
	flake8 src/ tests/ --max-line-length=100

format:
	black src/ tests/
