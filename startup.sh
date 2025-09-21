#!/bin/bash

# Azure App Service startup script
echo "=== Azure App Service Startup ==="
echo "Current directory: $(pwd)"
echo "Python version: $(python3 --version)"

# Change to the app directory
cd /home/site/wwwroot

echo "Changed to app directory: $(pwd)"
echo "Files in app directory:"
ls -la

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo "ERROR: app.py not found in /home/site/wwwroot!"
    echo "Available files:"
    ls -la
    exit 1
fi

# Set environment variables
export STREAMLIT_SERVER_PORT=8000
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
export STREAMLIT_SERVER_ENABLE_CORS=true
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false

echo "Starting Streamlit application..."
python3 -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0