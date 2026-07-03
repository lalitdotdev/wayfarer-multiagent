# Contributing to Wayfarer

Thank you for considering contributing to Wayfarer! This document outlines the AI-powered multi-agent travel concierge!

## How to Contribute

### Reporting Bugs

Before submitting a bug report, please check if it has already been reported by searching the Issues tab.

When reporting a bug, please include:
- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Screenshots or screen recordings if applicable
- Your environment (browser version, OS, etc.)
- Any relevant error messages from the console

### Suggesting Features

Feature requests are welcome! Please consider:
- Whether the feature aligns with the project's scope and vision
- How the feature would benefit users
- Any potential implementation considerations
- Check if similar features have been requested before

### Contributing Code

1. Fork the repository on GitHub
2. Clone your fork locally: `git clone https://github.com/yourusername/wayfarer.git`
3. Create a new branch for your feature or fix: `git checkout -b feature/amazing-feature`
4. Make your changes following the coding standards below
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request against the main branch

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- PostgreSQL database
- API keys for external services (Groq, AviationStack, Tavily)

### Installation

1. Clone the repository: `git clone https://github.com/yourusername/wayfarer.git`
2. Navigate to the project directory: `cd wayfarer`
3. Create a virtual environment: `python -m venv venv`
4. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
5. Install dependencies: `pip install -r requirements.txt`
6. Set up environment variables:
   - Copy `.env.example` to `.env` and fill in your API keys
   - Get your API keys from:
     - Groq: https://console.groq.com/
     - AviationStack: https://aviationstack.com/
     - Tavily: https://tavily.com/
     - PostgreSQL: Your database connection string

### Coding Standards

- Follow PEP 8 for Python code style
- Use descriptive variable and function names
- Write clear, concise docstrings for all public functions and classes
- Add type hints where possible
- Keep functions focused and under 50 lines when possible
- Write tests for new functionality
- Run `flake8` and `black` before submitting PRs

### Testing

- Run tests with: `pytest`
- Run tests with coverage: `pytest --cov=./`
- Ensure new code includes adequate test coverage
- Tests should be placed in the `tests/` directory

### Pull Request Process

1. Update the README.md with details of changes if applicable
2. Update documentation as needed
3. The PR will be reviewed by maintainers
4. Address any feedback or requested changes
5. Once approved, maintainers will merge the PR

### Community

- Please be respectful and considerate of others
- Follow the Python Community Code of Conduct
- Help answer questions in issues when you can
- Suggest improvements to the contribution process

Thank you for contributing to Wayfarer!