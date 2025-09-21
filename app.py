#!/usr/bin/env python3
"""
Alternative entry point for Azure App Service.
This file imports and runs the main Streamlit application.
"""

import os
import sys

# Add the current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Set environment variables for Streamlit
os.environ.setdefault('STREAMLIT_SERVER_PORT', '8000')
os.environ.setdefault('STREAMLIT_SERVER_ADDRESS', '0.0.0.0')
os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
os.environ.setdefault('STREAMLIT_BROWSER_GATHER_USAGE_STATS', 'false')

if __name__ == "__main__":
    # Import and run the main Streamlit app
    try:
        import streamlit.web.cli as stcli
        import streamlit
        
        print(f"🚀 Starting Streamlit v{streamlit.__version__}")
        print(f"📁 Working directory: {os.getcwd()}")
        print(f"🐍 Python: {sys.executable}")
        
        # Run Streamlit with the main application file
        sys.argv = [
            "streamlit",
            "run",
            "streamlit.py",
            "--server.port=8000",
            "--server.address=0.0.0.0",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]
        
        stcli.main()
        
    except ImportError as e:
        print(f"❌ Error importing Streamlit: {e}")
        print("📦 Attempting to install Streamlit...")
        
        import subprocess
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'streamlit'])
            print("✅ Streamlit installed successfully")
            
            # Try again
            import streamlit.web.cli as stcli
            sys.argv = [
                "streamlit",
                "run", 
                "streamlit.py",
                "--server.port=8000",
                "--server.address=0.0.0.0",
                "--server.headless=true",
                "--browser.gatherUsageStats=false"
            ]
            stcli.main()
            
        except Exception as install_error:
            print(f"❌ Failed to install Streamlit: {install_error}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)