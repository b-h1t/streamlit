#!/usr/bin/env python3
"""
Simple startup script that uses the virtual environment directly.
"""

import os
import sys
import subprocess

def main():
    """Start the Streamlit application using the virtual environment."""
    
    print("🚀 Starting Streamlit application on Azure...")
    
    # Change to the correct directory
    os.chdir('/home/site/wwwroot')
    print(f"Working directory: {os.getcwd()}")
    
    # Use the virtual environment Python
    venv_python = '/home/site/wwwroot/antenv/bin/python'
    
    if os.path.exists(venv_python):
        print(f"✅ Using virtual environment Python: {venv_python}")
        python_cmd = venv_python
    else:
        print("❌ Virtual environment not found, using system Python")
        python_cmd = sys.executable
    
    # Set environment variables
    os.environ['STREAMLIT_SERVER_PORT'] = '8000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Command to run Streamlit
    cmd = [
        python_cmd, '-m', 'streamlit', 'run', 'streamlit_app.py',
        '--server.port', '8000',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
