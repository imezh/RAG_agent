#!/bin/bash
set -e

echo "Checking Python version..."
python --version

# Verify we're using Python 3.11
PYTHON_VERSION=$(python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if [[ ! "$PYTHON_VERSION" =~ ^3\.11 ]]; then
    echo "ERROR: Python 3.11 is required, but found $PYTHON_VERSION"
    exit 1
fi

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
