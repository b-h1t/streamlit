#!/usr/bin/env python3
"""
WSGI application that runs Streamlit on Azure.
This provides a bridge between Azure's WSGI expectations and Streamlit.
"""

import os
import sys
import subprocess
import threading
import time
import requests
from urllib.parse import urlparse

# Global variable to track if Streamlit is running
streamlit_running = False
streamlit_process = None

def start_streamlit():
    """Start Streamlit in a separate process."""
    global streamlit_running, streamlit_process
    
    if streamlit_running:
        return
    
    print("🚀 Starting Streamlit application...")
    
    # Set environment variables
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
    
    try:
        streamlit_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        streamlit_running = True
        print("✅ Streamlit started successfully")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        streamlit_running = False

def application(environ, start_response):
    """WSGI application that serves Streamlit."""
    
    global streamlit_running, streamlit_process
    
    # Start Streamlit if not already running
    if not streamlit_running:
        start_streamlit()
        # Wait a moment for Streamlit to start
        time.sleep(3)
    
    # Get the request path
    path = environ.get('PATH_INFO', '/')
    
    # If Streamlit is running, proxy the request
    if streamlit_running and streamlit_process and streamlit_process.poll() is None:
        try:
            # Forward the request to Streamlit
            streamlit_url = f"http://localhost:8000{path}"
            response = requests.get(streamlit_url, timeout=10)
            
            # Set response headers
            status = f"{response.status_code} {response.reason}"
            headers = [
                ('Content-type', response.headers.get('content-type', 'text/html')),
                ('Content-Length', str(len(response.content)))
            ]
            start_response(status, headers)
            
            return [response.content]
            
        except Exception as e:
            print(f"Error proxying to Streamlit: {e}")
            # Fall through to error page
    
    # Fallback: Show loading page
    status = '200 OK'
    headers = [('Content-type', 'text/html; charset=utf-8')]
    start_response(status, headers)
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document Assignment & Labelling</title>
        <style>
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 0;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .container {{ 
                max-width: 800px; 
                margin: 0 auto; 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
            }}
            .loading {{
                color: #007bff;
                font-size: 1.2em;
                margin: 20px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Document Assignment & Labelling</h1>
            <div class="loading">
                <p>🔄 Starting Streamlit application...</p>
                <p>Please wait while the app loads.</p>
            </div>
            <p>If this page doesn't refresh automatically, please reload the page.</p>
            <script>
                setTimeout(function() {{
                    location.reload();
                }}, 5000);
            </script>
        </div>
    </body>
    </html>
    """
    
    return [html.encode('utf-8')]

# This is the WSGI application object that Azure expects
app = application

if __name__ == '__main__':
    print("WSGI Streamlit application is ready")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
