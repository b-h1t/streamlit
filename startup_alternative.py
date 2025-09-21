#!/usr/bin/env python3
"""
Alternative startup script for Azure App Service.
This version uses a more direct approach to start Streamlit.
"""

import os
import sys
import subprocess
import time

def main():
    """Start the Streamlit application with proper configuration."""
    print("=== Alternative Streamlit Startup ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    # Check if app.py exists
    if not os.path.exists('app.py'):
        print("ERROR: app.py not found!")
        sys.exit(1)
    
    # Set environment variables
    env = os.environ.copy()
    env.update({
        'STREAMLIT_SERVER_PORT': '8000',
        'STREAMLIT_SERVER_ADDRESS': '0.0.0.0',
        'STREAMLIT_SERVER_HEADLESS': 'true',
        'STREAMLIT_BROWSER_GATHER_USAGE_STATS': 'false',
        'STREAMLIT_SERVER_ENABLE_CORS': 'true',
        'STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION': 'false'
    })
    
    print("Environment variables set:")
    for key, value in env.items():
        if key.startswith('STREAMLIT_'):
            print(f"  {key}={value}")
    
    # Build the command
    cmd = [
        sys.executable, '-m', 'streamlit', 'run', 'app.py',
        '--server.port', '8000',
        '--server.address', '0.0.0.0',
        '--server.headless', 'true',
        '--browser.gatherUsageStats', 'false',
        '--server.enableCORS', 'true',
        '--server.enableXsrfProtection', 'false'
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        # Start the process
        process = subprocess.Popen(cmd, env=env)
        
        # Wait a moment for startup
        time.sleep(2)
        
        # Check if process is still running
        if process.poll() is None:
            print("✅ Streamlit started successfully!")
            print("✅ App should be available at http://0.0.0.0:8000")
            
            # Keep the process running
            process.wait()
        else:
            print("❌ Streamlit failed to start")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
