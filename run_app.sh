#!/bin/bash

# Exit on error
set -e

echo "--- Setting up NATS Environment ---"

# 1. Determine Python version (Prefer 3.11, fallback to 3.10, then 3)
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3.10 &> /dev/null; then
    PYTHON_CMD="python3.10"
else
    PYTHON_CMD="python3"
fi

echo "Using Python interpreter: $PYTHON_CMD"

# Check if version is 3.13 (known to cause issues with current Spacy/Blis)
PY_VER=$($PYTHON_CMD --version)
if [[ "$PY_VER" == *"3.13"* ]]; then
    echo "WARNING: Detected Python 3.13. This version is known to have compatibility issues with Spacy/Blis."
    echo "Please install Python 3.11 (e.g., 'brew install python@3.11') for best results."
    echo "Attempting to proceed, but installation may fail..."
fi

# 2. Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
else
    echo "Virtual environment already exists."
fi

# 2. Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# 3. Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# 4. Install Spacy models
echo "Installing Spacy models..."
python -m spacy download en_core_web_sm
# Attempt to install Greek model, but don't fail if it errors (optional)
python -m spacy download el_core_news_md || echo "Greek model installation failed, falling back to English only."

# 5. Run the application
echo "Starting application..."
python wsgi.py
