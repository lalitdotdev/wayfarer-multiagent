.PHONY: help install test lint format clean docker-build docker-run

help:
	@echo "Available targets:"
	@echo "  install     - Install development dependencies"
	@echo "  test        - Run test suite"
	@echo "  lint        - Run linter (flake8)"
	@echo "  format      - Format code with black"
	@echo "  clean       - Remove build artifacts and caches"
	@echo "  docker-build- Build Docker image"
	@echo "  docker-run  - Run Docker container"
	@echo

install:
	pip install -r requirements.txt
	pip install pytest pytest-cov flake8 black

test:
	pytest tests/ -v --cov=./ --cov-report=html

lint:
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

format:
	black .

clean:
	rm -rf __pycache__ */__pychat__ */*/__pycache__
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