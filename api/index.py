"""
Docker entry point for the Juvenile Immigration API
"""
import os
import threading
from flask import Flask
from flask_cors import CORS

from api.api_routes import (
    health, get_overview, representation_outcomes, 
    time_series_analysis, chi_square_analysis, outcome_percentages, countries_chart,
    meta_options, get_filtered_overview, data_status, force_reload_data, contact
)
from api.basic_stats import get_basic_statistics
from api.models import cache
from api.data_loader import load_data

# Create Flask app
app = Flask(__name__)

# Pre-load data on application startup to avoid per-request loading
def initialize_data():
    """Load data once when the application starts"""
    print("🚀 Initializing data on application startup...")
    if not cache.is_loaded():
        load_data()
    print("✅ Application initialization complete")

# Initialize data in a background thread to avoid blocking startup
threading.Thread(target=initialize_data, daemon=True).start()

# Configure CORS - temporarily allow all origins to fix CORS issues
CORS(app, 
     origins="*",  # Allow all origins temporarily
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept', 'X-Requested-With'],
     supports_credentials=False)

# Pre-load data in background thread when app starts
_data_loading_lock = threading.Lock()
_data_loaded = False

def initialize_data():
    """Initialize data loading in background thread"""
    global _data_loaded
    with _data_loading_lock:
        if not _data_loaded:
            print("🚀 Initializing data loading...")
            try:
                load_data()
                _data_loaded = True
                print("✅ Data initialization completed")
            except Exception as e:
                print(f"❌ Data initialization failed: {e}")

# Start data loading in background thread
data_thread = threading.Thread(target=initialize_data, daemon=True)
data_thread.start()

app.add_url_rule('/health', 'health', health, methods=['GET'])
app.add_url_rule('/api/overview', 'get_overview', get_overview, methods=['GET'])
app.add_url_rule('/api/overview/filtered', 'get_filtered_overview', get_filtered_overview, methods=['GET'])
app.add_url_rule('/api/data/basic-stats', 'basic_stats', get_basic_statistics, methods=['GET'])
app.add_url_rule('/api/findings/representation-outcomes', 'representation_outcomes', representation_outcomes, methods=['GET'])
app.add_url_rule('/api/findings/time-series', 'time_series_analysis', time_series_analysis, methods=['GET'])
app.add_url_rule('/api/findings/chi-square', 'chi_square_analysis', chi_square_analysis, methods=['GET'])
app.add_url_rule('/api/findings/outcome-percentages', 'outcome_percentages', outcome_percentages, methods=['GET'])
app.add_url_rule('/api/findings/countries', 'countries_chart', countries_chart, methods=['GET'])
app.add_url_rule('/api/meta/options', 'meta_options', meta_options, methods=['GET'])
app.add_url_rule('/api/data-status', 'data_status', data_status, methods=['GET'])
app.add_url_rule('/api/force-reload-data', 'force_reload_data', force_reload_data, methods=['POST'])
app.add_url_rule('/api/contact', 'contact', contact, methods=['POST', 'OPTIONS'])

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)