#!/bin/bash

# Exit on any failure
set -e

echo "🚀 Starting Azure deployment script..."

# Verify Python version
echo "Python version:"
python --version

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install requirements
echo "📦 Installing Python packages..."
python -m pip install -r requirements.txt

# Verify Streamlit installation
echo "✅ Verifying Streamlit installation..."
python -c "import streamlit; print('Streamlit version:', streamlit.__version__)"

# List installed packages
echo "📋 Installed packages:"
pip list

echo "✅ Deployment script completed successfully!"
