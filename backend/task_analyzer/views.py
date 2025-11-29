import os
from django.http import HttpResponse, FileResponse
from django.conf import settings

def serve_frontend(request):
    """Serve the frontend index.html file"""
    frontend_path = os.path.join(settings.BASE_DIR, '../frontend/index.html')
    try:
        with open(frontend_path, 'r', encoding='utf-8') as f:
            return HttpResponse(f.read(), content_type='text/html')
    except FileNotFoundError:
        return HttpResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Smart Task Analyzer</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
                .container { max-width: 600px; margin: 0 auto; }
                .error { background: #ffeaa7; padding: 20px; border-radius: 8px; margin: 20px 0; }
                .success { background: #55efc4; padding: 15px; border-radius: 8px; margin: 20px 0; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Smart Task Analyzer</h1>
                <div class="error">
                    <h3>Frontend Files Not Found</h3>
                    <p>The frontend files (index.html, styles.css, script.js) could not be found in the frontend directory.</p>
                    <p>Please make sure the frontend directory exists and contains the required files.</p>
                </div>
                <div class="success">
                    <h3>Backend API is Working!</h3>
                    <p>Test the API: <a href="/api/info/" target="_blank">API Info</a></p>
                    <p>Test task analysis: <a href="/api/tasks/suggest/" target="_blank">Task Suggestions</a></p>
                </div>
            </div>
        </body>
        </html>
        """, status=404)