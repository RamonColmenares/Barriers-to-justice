"""
Main entry point for the juvenile immigration API
This file serves as the main entry point that can be referenced from both dev.sh and deploy.sh
"""
import os
from api.index import app
from api.config import DEBUG

# Vercel serverless function handler
def handler(request, context):
    """Vercel handler function"""
    with app.app_context():
        return app(request.environ, lambda status, headers: None)

if __name__ == '__main__':
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    
    print("🚀 Starting Juvenile Immigration API server from main.py...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"🩺 Health check: http://{host}:{port}/api/health")
    print(f"📊 Overview endpoint: http://{host}:{port}/api/overview")
    print(f"📊 Basic stats endpoint: http://{host}:{port}/api/data/basic-stats")
    print(f"🐍 Debug mode: {DEBUG}")
    
    app.run(host=host, port=port, debug=DEBUG)
