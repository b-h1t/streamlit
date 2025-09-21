#!/usr/bin/env python3
"""
Startup script for Streamlit on Azure App Service.
This runs the actual Streamlit application.
"""

import os
import sys
import subprocess

def main():
    """Start the Streamlit application."""
    
    print("🚀 Starting Streamlit application on Azure...")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("Files in directory:", os.listdir('.'))
    
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = '8000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Command to run Streamlit
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
        '--server.port', '8000',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Run Streamlit
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("Streamlit stopped by user")
        sys.exit(0)

if __name__ == '__main__':
    main()
