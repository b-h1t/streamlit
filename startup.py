#!/usr/bin/env python3
"""
Simple startup script for Azure App Service.
This runs the Streamlit application directly.
"""

import os
import sys
import subprocess

def main():
    """Start the Streamlit application."""
    
    print("🚀 Starting Streamlit application on Azure...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Working directory: {os.getcwd()}")
    print("Files in directory:", os.listdir('.'))
    
    # Change to the correct directory (only on Azure)
    if os.path.exists('/home/site/wwwroot'):
        os.chdir('/home/site/wwwroot')
        print(f"Changed to Azure directory: {os.getcwd()}")
    else:
        print(f"Running locally in directory: {os.getcwd()}")
    
    # Try to find the correct Python executable
    python_paths = [
        '/home/site/wwwroot/antenv/bin/python',  # Azure virtual env
        '/tmp/oryx/platforms/python/3.11.13/bin/python3.11',  # Azure Oryx
        '/opt/python/3.11/bin/python3.11',  # Azure system Python
        '/opt/python/3/bin/python3',  # Azure system Python
        sys.executable  # Current Python (works locally and Azure)
    ]
    
    working_python = None
    for python_path in python_paths:
        if os.path.exists(python_path):
            print(f"Found Python at: {python_path}")
            # Test if streamlit is available
            try:
                result = subprocess.run([python_path, '-c', 'import streamlit; print("Streamlit available")'], 
                                     capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    working_python = python_path
                    print(f"✅ Streamlit is available with {python_path}")
                    break
                else:
                    print(f"❌ Streamlit not available with {python_path}: {result.stderr}")
            except Exception as e:
                print(f"❌ Error testing {python_path}: {e}")
    
    if not working_python:
        print("❌ No working Python with Streamlit found!")
        print("Available Python paths:")
        for path in python_paths:
            exists = "✅" if os.path.exists(path) else "❌"
            print(f"  {exists} {path}")
        
        # Try to install streamlit in the current environment
        print("🔧 Attempting to install Streamlit...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'streamlit'], check=True)
            working_python = sys.executable
            print("✅ Streamlit installed successfully")
        except Exception as e:
            print(f"❌ Failed to install Streamlit: {e}")
            return
    
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = '8000'
    os.environ['STREAMLIT_SERVER_ADDRESS'] = '0.0.0.0'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'
    
    # Check if streamlit.py exists (your main file)
    if not os.path.exists('streamlit.py'):
        print("❌ streamlit.py not found!")
        print("Available files:", os.listdir('.'))
        return
    
    # Command to run Streamlit
    cmd = [
        working_python, '-m', 'streamlit', 'run', 'streamlit.py',
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