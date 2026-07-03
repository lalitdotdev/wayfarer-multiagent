# Contributing to Wayfarer

Thank you for considering contributing to Wayfarer! This document outlines the process for contributing to this project.

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
   - Copy `.env.example` to `.env`
   - Fill in your API keys and database URL
7. Initialize the database: The application will automatically create tables on first run
8. Run the application: `streamlit run app.py`

### Coding Standards
- Follow PEP 8 for Python code style
- Use descriptive variable and function names
- Add docstrings to all public functions and classes
- Keep functions focused and under 50 lines when possible
- Use type hints for function parameters and return values
- Write clear, concise comments explaining complex logic
- Format strings using f-strings (Python 3.6+)
- Handle exceptions appropriately rather than using broad except clauses

### Git Commit Guidelines
- Use the imperative mood in commit messages ("Add feature" not "Added feature")
- Keep the subject line under 50 characters
- Provide a detailed explanation in the commit body when needed
- Reference related issues: "Fixes #123" or "See #456"
- Make commits atomic and focused on a single change

### Pull Request Process
1. Ensure your code passes any existing tests
2. Update documentation as needed
3. The PR description should clearly explain the changes and their purpose
4. Include screenshots for UI changes
5. Link to any related issues
6. Request review from maintainers
7. Address any feedback promptly
8. Once approved, your PR will be merged

## Code of Conduct
Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms.

## Getting Help
If you need help with your contribution:
- Check the existing documentation
- Look through past issues and pull requests
- Ask for clarification in the issue discussion
- Maintainers are available to help guide newcomers

Thank you for contributing to Wayfarer!