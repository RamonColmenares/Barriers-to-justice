"""
Main Flask application entry point for the juvenile immigration API
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from functools import wraps

from api.api_routes import (
    health,
    meta_options,
    get_overview,
    load_data_endpoint,
    force_reload_data,
    data_status,
    representation_outcomes,
    time_series_analysis,
    chi_square_analysis,
    outcome_percentages,
    countries_chart,
    basic_statistics,
    get_filtered_overview,
    get_all_findings_data,
    contact
)

from api.config import DEBUG

def handle_preflight(f):
    """Decorator to handle preflight OPTIONS requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            # Handle preflight request
            response = jsonify({'status': 'OK'})
            
            # Get the origin from the request
            origin = request.headers.get('Origin')
            allowed_origins = [
                'https://d2qqofrfkbwcrl.cloudfront.net',
                'https://54-84-88-142.sslip.io',
                'http://localhost:3000',
                'http://localhost:5173'
            ]
            
            # Check if origin is allowed
            if origin in allowed_origins:
                response.headers.add('Access-Control-Allow-Origin', origin)
            else:
                response.headers.add('Access-Control-Allow-Origin', 'https://d2qqofrfkbwcrl.cloudfront.net')
            
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            response.headers.add('Access-Control-Max-Age', '3600')
            return response
        return f(*args, **kwargs)
    return decorated_function

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS to allow frontend communication
    # Allow both CloudFront and direct EC2 access
    allowed_origins = [
        'https://d2qqofrfkbwcrl.cloudfront.net',
        'https://54-84-88-142.sslip.io',  # Current EC2 IP
        'http://localhost:3000',  # For local development
        'http://localhost:5173'   # For Vite dev server
    ]

    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'OPTIONS'], 
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=False,
         send_wildcard=False,
         automatic_options=True)
    
    # Configuration
    app.config['DEBUG'] = DEBUG
    
    # Register routes
    app.route('/health', methods=['GET'])(health)  # For deployment health checks
    app.route('/api/health', methods=['GET'])(health)
    app.route('/api/meta/options', methods=['GET'])(meta_options)
    app.route('/api/overview', methods=['GET'])(get_overview)
    app.route('/api/load-data', methods=['POST'])(load_data_endpoint)
    app.route('/api/force-reload', methods=['POST'])(force_reload_data)
    app.route('/api/status', methods=['GET'])(data_status)
    app.route('/api/findings/representation-outcomes', methods=['GET', 'POST', 'OPTIONS'])(handle_preflight(representation_outcomes))
    app.route('/api/findings/time-series', methods=['GET', 'POST', 'OPTIONS'])(handle_preflight(time_series_analysis))
    app.route('/api/findings/chi-square', methods=['GET', 'POST', 'OPTIONS'])(handle_preflight(chi_square_analysis))
    app.route('/api/findings/outcome-percentages', methods=['GET', 'POST', 'OPTIONS'])(handle_preflight(outcome_percentages))
    app.route('/api/findings/countries', methods=['GET', 'POST', 'OPTIONS'])(handle_preflight(countries_chart))
    app.route('/api/data/basic-stats', methods=['GET', 'POST', 'OPTIONS'])(handle_preflight(basic_statistics))
    app.route('/api/filtered-overview', methods=['GET', 'POST'])(get_filtered_overview)
    app.route('/api/findings', methods=['GET', 'POST'])(get_all_findings_data)
    app.route('/api/contact', methods=['POST'])(contact)
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    contact_email = os.getenv('CONTACT_EMAIL', 'not-set')
    
    print(f"🚀 Starting Juvenile Immigration API server...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"📧 Contact email configured: {contact_email}")
    print(f"🩺 Health check: http://{host}:{port}/health")
    print(f"🩺 API Health check: http://{host}:{port}/api/health")
    print(f"📊 Overview endpoint: http://{host}:{port}/api/overview")
    print(f"📊 Basic stats endpoint: http://{host}:{port}/api/data/basic-stats")
    
    app.run(host=host, port=port, debug=DEBUG)
