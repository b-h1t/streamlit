#!/usr/bin/env python3
"""
WSGI application for Azure deployment.
"""

def application(environ, start_response):
    """Simple WSGI application."""
    
    status = '200 OK'
    headers = [('Content-type', 'text/html')]
    start_response(status, headers)
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Document Assignment & Labelling</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
            .container { max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📄 Document Assignment & Labelling</h1>
            <p>✅ Azure deployment is working!</p>
            <p>This is a placeholder page.</p>
        </div>
    </body>
    </html>
    """
    
    return [html.encode()]

if __name__ == '__main__':
    print("WSGI app is ready")
