#!/bin/bash
# Startup script that activates the virtual environment and runs Streamlit

echo "🚀 Starting Streamlit application on Azure..."

# Change to the correct directory
cd /home/site/wwwroot
echo "Working directory: $(pwd)"

# Activate the virtual environment
if [ -f "/home/site/wwwroot/antenv/bin/activate" ]; then
    echo "✅ Activating virtual environment..."
    source /home/site/wwwroot/antenv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ Virtual environment not found at /home/site/wwwroot/antenv/bin/activate"
    echo "Available files:"
    ls -la /home/site/wwwroot/
fi

# Set environment variables
export STREAMLIT_SERVER_PORT=8000
export STREAMLIT_SERVER_ADDRESS=0.0.0.0
export STREAMLIT_SERVER_HEADLESS=true
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# Check if streamlit_app.py exists
if [ ! -f "streamlit_app.py" ]; then
    echo "❌ streamlit_app.py not found!"
    echo "Available files:"
    ls -la
    exit 1
fi

# Run Streamlit
echo "🚀 Starting Streamlit..."
python -m streamlit run streamlit_app.py \
    --server.port 8000 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false
