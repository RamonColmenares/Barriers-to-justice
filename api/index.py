"""
Main Flask application entry point for the juvenile immigration API
"""
from flask import Flask
from flask_cors import CORS
import os

# Import route handlers
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

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Enable CORS for all routes
    CORS(app)
    
    # Configuration
    app.config['DEBUG'] = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Register routes
    app.route('/api/health', methods=['GET'])(health)
    app.route('/api/meta/options', methods=['GET'])(meta_options)
    app.route('/api/overview', methods=['GET'])(get_overview)
    app.route('/api/load-data', methods=['POST'])(load_data_endpoint)
    app.route('/api/force-reload', methods=['POST'])(force_reload_data)
    app.route('/api/status', methods=['GET'])(data_status)
    app.route('/api/representation-outcomes', methods=['POST'])(representation_outcomes)
    app.route('/api/time-series', methods=['POST'])(time_series_analysis)
    app.route('/api/chi-square', methods=['POST'])(chi_square_analysis)
    app.route('/api/outcome-percentages', methods=['POST'])(outcome_percentages)
    app.route('/api/countries', methods=['POST'])(countries_chart)
    app.route('/api/basic-stats', methods=['POST'])(basic_statistics)
    app.route('/api/filtered-overview', methods=['POST'])(get_filtered_overview)
    app.route('/api/findings', methods=['POST'])(get_all_findings_data)
    app.route('/api/contact', methods=['POST'])(contact)
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable or default to 5000
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting Juvenile Immigration API server...")
    print(f"🌐 Server will be available at: http://{host}:{port}")
    print(f"🩺 Health check: http://{host}:{port}/api/health")
    print(f"📊 Overview endpoint: http://{host}:{port}/api/overview")
    
    app.run(host=host, port=port, debug=debug)
