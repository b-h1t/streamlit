#!/usr/bin/env python3
"""
WSGI application for Azure deployment.
This is the main entry point for Azure App Service.
"""

import os
import sys

def application(environ, start_response):
    """WSGI application that serves the Document Assignment & Labelling app."""
    
    # Get the request path
    path = environ.get('PATH_INFO', '/')
    
    # Set response headers
    status = '200 OK'
    headers = [
        ('Content-type', 'text/html; charset=utf-8'),
        ('Cache-Control', 'no-cache, no-store, must-revalidate'),
        ('Pragma', 'no-cache'),
        ('Expires', '0')
    ]
    start_response(status, headers)
    
    # Create the HTML response
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
            h1 {{ 
                color: #333; 
                margin-bottom: 20px;
                font-size: 2.5em;
            }}
            .success {{ 
                color: #28a745; 
                font-size: 1.2em;
                margin: 20px 0; 
                font-weight: bold;
            }}
            .info {{ 
                color: #666; 
                margin: 20px 0; 
                line-height: 1.6;
            }}
            .status {{
                background: #e8f5e8;
                border: 1px solid #28a745;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
            }}
            .next-steps {{
                background: #f8f9fa;
                border-left: 4px solid #007bff;
                padding: 15px;
                margin: 20px 0;
                text-align: left;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Document Assignment & Labelling</h1>
            
            <div class="status">
                <p class="success">✅ Azure deployment is working!</p>
                <p class="info">Your application is successfully deployed and running on Azure App Service.</p>
            </div>
            
            <div class="next-steps">
                <h3>Next Steps:</h3>
                <ul>
                    <li>✅ Azure App Service is running</li>
                    <li>✅ Python environment is configured</li>
                    <li>✅ WSGI application is working</li>
                    <li>🔄 Configure Streamlit deployment</li>
                </ul>
            </div>
            
            <p class="info">
                <strong>Path:</strong> {path}<br>
                <strong>Python Version:</strong> {sys.version}<br>
                <strong>Working Directory:</strong> {os.getcwd()}
            </p>
        </div>
    </body>
    </html>
    """
    
    return [html.encode('utf-8')]

# This is the WSGI application object that Azure expects
app = application

# This is required for Azure
if __name__ == '__main__':
    print("WSGI application is ready for Azure deployment")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print("Files in directory:", os.listdir('.'))