.PHONY: help install test lint format clean test-coverage security-check docker-build docker-run run

help:
	@echo "Available targets:"
	@echo "  install         - Install development dependencies"
	@echo "  test            - Run test suite"
	@echo "  test-coverage   - Run tests with coverage report"
	@echo "  lint            - Run linter (flake8)"
	@echo "  format          - Format code with black"
	@echo "  security-check  - Run security scanning tools"
	@echo "  clean           - Remove build artifacts and caches"
	@echo "  docker-build    - Build Docker image"
	@echo "  docker-run      - Run Docker container"
	@echo "  run             - Run the application locally"
	@echo

install:
	pip install --upgrade pip
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v

test-coverage:
	pytest tests/ -v --cov=./ --cov-report=html --cov-report=term-missing

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format:
	black .
	isad .  # This will fail if isort is not installed, but we have it in requirements-dev.txt

security-check:
	safety check --full-report
	bandit -r . -f json -o security-report.json

clean:
	rm -rf __pycache__ */__pycache__ */*/__pycache__
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf build dist *.egg-info
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -exec rm -rf {} +

docker-build:
	docker build -t wayfarer .

docker-run:
	docker run -p 8501:8501 \
	  -e GROQ_API_KEY=$(GROQ_API_KEY) \
	  -e AVIATIONSTACK_API_KEY=$(AVIATIONSTACK_API_KEY) \
	  -e TAVILY_API_KEY=$(TAVILY_API_KEY) \
	  -e DATABASE_URL=$(DATABASE_URL) \
	  wayfarer

run:
	streamlit run app.py