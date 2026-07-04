#!/bin/bash
# Setup script for Wayfarer development environment

echo "Setting up Wayfarer development environment..."

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1-2)
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ] && [ "$PYTHON_VERSION" != "$REQUIRED_VERSION" ]; then
    if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" = "$REQUIRED_VERSION" ]; then
        echo "Error: Python $REQUIRED_VERSION or higher is required. You have $PYTHON_VERSION."
        exit 1
    fi
fi

echo "Python version: $PYTHON_VERSION (OK)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
if [ -f "requirements-dev.txt" ]; then
    echo "Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Install pre-commit hooks
if [ -f ".pre-commit-config.yaml" ]; then
    echo "Installing pre-commit hooks..."
    pre-commit install
fi

# Create .env file from example if it doesn't exist
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env to add your API keys"
elif [ ! -f ".env" ]; then
    echo "Creating .env file..."
    touch .env
    echo "Please add your API keys to .env"
fi

# Create necessary directories
mkdir -p travel_plans
mkdir -p logs

echo "Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run the application:"
echo "  streamlit run app.py"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To run tests with coverage:"
echo "  pytest --cov=./"
echo ""
echo "Happy coding!"