#!/bin/bash

echo "=========================================="
echo "Python Virtual Environment Setup (Linux)"
echo "=========================================="

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python3."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip inside venv
python -m pip install --upgrade pip

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "Virtual environment ready."
echo "To activate later, run:"
echo "    source venv/bin/activate"
echo ""
echo "Starting bash with custom prompt..."

# Launch bash with venv activated and custom prompt
bash --rcfile <(echo ". venv/bin/activate; PS1='<econ> \w> '")
