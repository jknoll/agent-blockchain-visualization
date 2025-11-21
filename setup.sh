#!/bin/bash
# Setup script for Blockchain Incident Visualization Agent

echo "=================================="
echo "Setting up Blockchain Incident Visualization Agent"
echo "=================================="
echo

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.9 or higher"
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi
echo

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source venv/bin/activate
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo "✓ Dependencies installed"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo
    echo "IMPORTANT: Please edit .env and add your API keys:"
    echo "  - ANTHROPIC_API_KEY (required)"
    echo "  - TRM_API_KEY (optional)"
    echo
else
    echo "✓ .env file already exists"
    echo
fi

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    mkdir output
    echo "✓ Output directory created"
fi

echo "=================================="
echo "Setup complete!"
echo "=================================="
echo
echo "Next steps:"
echo "1. Edit .env and add your ANTHROPIC_API_KEY"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python run.py"
echo
echo "For more information, see README.md"
