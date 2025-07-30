"""
Docker entry point for the Juvenile Immigration API
"""
import os
from flask import Flask
from flask_cors import CORS

# Import the API routes
try:
    from api.api_routes import (
        health, get_overview, representation_outcomes, 
        time_series_analysis, chi_square_analysis, outcome_percentages, countries_chart
    )
    from api.basic_stats import get_basic_statistics
    from api.models import cache
except ImportError:
    from api_routes import (
        health, get_overview, representation_outcomes, 
        time_series_analysis, chi_square_analysis, outcome_percentages, countries_chart
    )
    from basic_stats import get_basic_statistics
    from models import cache

# Create Flask app
app = Flask(__name__)

# Configure CORS to allow frontend communication
# Allow both CloudFront and direct EC2 access
allowed_origins = [
    'https://d2qqofrfkbwcrl.cloudfront.net',
    'https://54-196-120-37.sslip.io',
    'http://localhost:3000',  # For local development
    'http://localhost:5173'   # For Vite dev server
]

CORS(app, 
     origins=allowed_origins,
     methods=['GET', 'POST', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=False)

# Register API routes with proper URL patterns matching frontend expectations
app.add_url_rule('/health', 'health', health, methods=['GET'])
app.add_url_rule('/api/overview', 'get_overview', get_overview, methods=['GET'])
app.add_url_rule('/api/data/basic-stats', 'basic_stats', get_basic_statistics, methods=['GET'])
app.add_url_rule('/api/representation-outcomes', 'representation_outcomes', representation_outcomes, methods=['GET'])
app.add_url_rule('/api/findings/time-series', 'time_series_analysis', time_series_analysis, methods=['GET'])
app.add_url_rule('/api/findings/chi-square', 'chi_square_analysis', chi_square_analysis, methods=['GET'])
app.add_url_rule('/api/findings/outcome-percentages', 'outcome_percentages', outcome_percentages, methods=['GET'])
app.add_url_rule('/api/findings/countries', 'countries_chart', countries_chart, methods=['GET'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
