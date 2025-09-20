#!/usr/bin/env python3
"""
Startup script for Azure App Service deployment
"""
import os
import subprocess
import sys

def main():
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = os.environ.get('PORT', '8501')
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Start Streamlit
    cmd = [sys.executable, '-m', 'streamlit', 'run', 'streamlit.py']
    subprocess.run(cmd)

if __name__ == '__main__':
    main()
