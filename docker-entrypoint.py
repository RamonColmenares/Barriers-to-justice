"""
Docker entry point for the Juvenile Immigration API
"""
import os
from flask import Flask
from flask_cors import CORS


from api.api_routes import (
    health, get_overview, representation_outcomes, 
    time_series_analysis, chi_square_analysis, outcome_percentages, countries_chart,
    meta_options, get_filtered_overview, load_data_endpoint, force_reload_data, 
    data_status, basic_statistics, get_all_findings_data, contact
)
from api.models import cache

# Create Flask app
app = Flask(__name__)

# Configure CORS to allow frontend communication
# Allow both CloudFront and direct EC2 access
import re
allowed_origins = [
    'https://d2qqofrfkbwcrl.cloudfront.net',
    'https://54-84-88-142.sslip.io',  # Updated IP from error logs
    'https://54-145-92-66.sslip.io',   # Keep old IP as backup
    'http://localhost:3000',  # For local development
    'http://localhost:5173'   # For Vite dev server
]

# For debugging CORS issues, temporarily allow all origins
# Remove this in production and use specific origins
CORS(app, 
     resources={r"/api/*": {"origins": "*"}}, 
     methods=['GET', 'POST', 'OPTIONS'], 
     allow_headers=['Content-Type', 'Authorization', 'Access-Control-Allow-Origin'], 
     supports_credentials=False)

# Register API routes with proper URL patterns matching frontend expectations
app.add_url_rule('/health', 'health', health, methods=['GET'])
app.add_url_rule('/api/health', 'api_health', health, methods=['GET'])
app.add_url_rule('/api/overview', 'get_overview', get_overview, methods=['GET'])
app.add_url_rule('/api/overview/filtered', 'filtered_overview', get_filtered_overview, methods=['GET'])
app.add_url_rule('/api/data/basic-stats', 'basic_stats', basic_statistics, methods=['GET'])
app.add_url_rule('/api/meta/options', 'meta_options', meta_options, methods=['GET'])
app.add_url_rule('/api/load-data', 'load_data', load_data_endpoint, methods=['GET'])
app.add_url_rule('/api/force-reload-data', 'force_reload', force_reload_data, methods=['GET'])
app.add_url_rule('/api/data-status', 'data_status', data_status, methods=['GET'])
app.add_url_rule('/api/findings/representation-outcomes', 'representation_outcomes', representation_outcomes, methods=['GET'])
app.add_url_rule('/api/findings/time-series', 'time_series_analysis', time_series_analysis, methods=['GET'])
app.add_url_rule('/api/findings/chi-square', 'chi_square_analysis', chi_square_analysis, methods=['GET'])
app.add_url_rule('/api/findings/outcome-percentages', 'outcome_percentages', outcome_percentages, methods=['GET'])
app.add_url_rule('/api/findings/countries', 'countries_chart', countries_chart, methods=['GET'])
app.add_url_rule('/api/findings/all', 'all_findings', get_all_findings_data, methods=['GET'])
app.add_url_rule('/api/contact', 'contact', contact, methods=['POST'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
