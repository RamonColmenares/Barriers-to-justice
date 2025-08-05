"""
Main Flask application entry point for the juvenile immigration API
"""
from flask import Flask
from flask_cors import CORS
import os

# Import route handlers
try:
    from .api_routes import (
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
    from .config import DEBUG
except ImportError:
    from api_routes import (
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
    from config import DEBUG

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure CORS to allow frontend communication
    # Allow both CloudFront and direct EC2 access
    allowed_origins = [
        'https://d2qqofrfkbwcrl.cloudfront.net',
        'https://54-145-92-66.sslip.io',
        'http://localhost:3000',  # For local development
        'http://localhost:5173'   # For Vite dev server
    ]

    CORS(app, 
         origins=allowed_origins,
         methods=['GET', 'POST', 'OPTIONS'], 
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=False)
    
    # Configuration
    app.config['DEBUG'] = DEBUG
    
    # Register routes
    app.route('/api/health', methods=['GET'])(health)
    app.route('/api/meta/options', methods=['GET'])(meta_options)
    app.route('/api/overview', methods=['GET'])(get_overview)
    app.route('/api/load-data', methods=['POST'])(load_data_endpoint)
    app.route('/api/force-reload', methods=['POST'])(force_reload_data)
    app.route('/api/status', methods=['GET'])(data_status)
    app.route('/api/findings/representation-outcomes', methods=['GET', 'POST', 'OPTIONS'])(representation_outcomes)
    app.route('/api/findings/time-series', methods=['GET', 'POST', 'OPTIONS'])(time_series_analysis)
    app.route('/api/findings/chi-square', methods=['GET', 'POST', 'OPTIONS'])(chi_square_analysis)
    app.route('/api/findings/outcome-percentages', methods=['GET', 'POST', 'OPTIONS'])(outcome_percentages)
    app.route('/api/findings/countries', methods=['GET', 'POST', 'OPTIONS'])(countries_chart)
    app.route('/api/data/basic-stats', methods=['GET', 'POST', 'OPTIONS'])(basic_statistics)
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
    
    print(f"🚀 Starting Juvenile Immigration API server...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"🩺 Health check: http://{host}:{port}/api/health")
    print(f"📊 Overview endpoint: http://{host}:{port}/api/overview")
    print(f"📊 Basic stats endpoint: http://{host}:{port}/api/data/basic-stats")
    
    app.run(host=host, port=port, debug=DEBUG)
