#!/bin/bash

# Exit on any error
set -e

echo "=== Starting Streamlit Application ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"
echo "Files in directory:"
ls -la

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found!"
    exit 1
fi

# Set environment variables
export STREAMLIT_SERVER_PORT=8000
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

echo "Environment variables set:"
echo "STREAMLIT_SERVER_PORT=$STREAMLIT_SERVER_PORT"
echo "STREAMLIT_SERVER_ADDRESS=$STREAMLIT_SERVER_ADDRESS"

echo "Starting Streamlit..."
python3 -m streamlit run app.py \
    --server.port 8000 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS true \
    --server.enableXsrfProtection false
