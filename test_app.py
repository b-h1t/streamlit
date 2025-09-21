#!/usr/bin/env python3
"""
Simple test app to verify Azure can run Python.
This will help diagnose if the issue is with Python execution or Streamlit specifically.
"""

import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Azure Test - Python Working</title>
        </head>
        <body>
            <h1>✅ Azure Python Test Successful!</h1>
            <p><strong>Python version:</strong> {sys.version}</p>
            <p><strong>Current directory:</strong> {os.getcwd()}</p>
            <p><strong>Files in directory:</strong> {', '.join(os.listdir('.'))}</p>
            <p><strong>Environment variables:</strong></p>
            <ul>
                <li>PORT: {os.environ.get('PORT', 'Not set')}</li>
                <li>PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}</li>
            </ul>
            <p><strong>If you see this page, Python is working correctly on Azure!</strong></p>
            <hr>
            <p><em>Next step: Test Streamlit deployment</em></p>
        </body>
        </html>
        """
        self.wfile.write(html.encode())
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def main():
    print("=== Starting Azure Test Server ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Files in directory: {os.listdir('.')}")
    
    port = int(os.environ.get('PORT', 8000))
    print(f"Starting server on port {port}")
    
    try:
        server = HTTPServer(('0.0.0.0', port), TestHandler)
        print(f"Server started successfully on port {port}")
        server.serve_forever()
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
