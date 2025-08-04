"""
Main Flask application for the juvenile immigration API
Refactored into modular components for better maintainability
"""
from flask import Flask
from flask_cors import CORS

# Import route handlers
from .api_routes import (
    health,
    get_overview,
    get_filtered_overview,
    load_data_endpoint,
    force_reload_data,
    data_status,
    representation_outcomes,
    time_series_analysis,
    chi_square_analysis,
    outcome_percentages,
    countries_chart,
    basic_statistics,
    meta_options
)
from .config import DEBUG

app = Flask(__name__)

# Configure CORS to allow frontend communication
# Allow both CloudFront and direct EC2 access
import os, re
frontend_origin = os.getenv('FRONTEND_ORIGIN')
allowed_origins = [
    origin for origin in [
        frontend_origin,
        'https://d2qqofrfkbwcrl.cloudfront.net',
        'http://localhost:3000',
        'http://localhost:5173'
    ] if origin
]
# allow any *.sslip.io origin dynamically by overriding CORS

CORS(app, resources={r"/api/*": {"origins": allowed_origins + [r"https://.*\.sslip\.io"]}}, methods=['GET', 'POST', 'OPTIONS'], allow_headers=['Content-Type', 'Authorization'], supports_credentials=False)

# Configuration
app.config['DEBUG'] = DEBUG

# Register routes
@app.route('/api/meta/options')
def meta_options_route():
    return meta_options()

@app.route('/api/health')
def health_route():
    return health()

@app.route('/api/overview')
def overview_route():
    return get_overview()

@app.route('/api/overview/filtered')
def filtered_overview_route():
    return get_filtered_overview()

@app.route('/api/load-data')
def load_data_route():
    return load_data_endpoint()

@app.route('/api/force-reload-data')
def force_reload_route():
    return force_reload_data()

@app.route('/api/data-status')
def data_status_route():
    return data_status()

@app.route('/api/findings/representation-outcomes')
def representation_outcomes_route():
    return representation_outcomes()

@app.route('/api/findings/time-series')
def time_series_route():
    return time_series_analysis()

@app.route('/api/findings/chi-square')
def chi_square_route():
    return chi_square_analysis()

@app.route('/api/findings/outcome-percentages')
def outcome_percentages_route():
    return outcome_percentages()

@app.route('/api/findings/countries')
def countries_chart_route():
    return countries_chart()

@app.route('/api/data/basic-stats')
def basic_statistics_route():
    return basic_statistics()

# Vercel serverless function handler
def handler(request, context):
    """Vercel handler function"""
    with app.app_context():
        return app(request.environ, lambda status, headers: None)

# For local development
if __name__ == '__main__':
    print("🚀 Starting development server...")
    print("🌐 Backend running on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=DEBUG)
