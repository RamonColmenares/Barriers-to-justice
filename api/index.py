"""
Docker entry point for the Juvenile Immigration API
"""
import os
import threading
import time
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

# Configure CORS for production - specific domains only to avoid memory overhead
CORS(app, 
     origins=[
         "https://d30ap9o2ygmovh.cloudfront.net",
         "https://d3f74pvoh6t7bv.cloudfront.net",
         "https://54-162-47-183.sslip.io",
         "http://54-162-47-183.sslip.io",
         "https://54-224-172-54.sslip.io",
         "http://54-224-172-54.sslip.io"
     ],
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization', 'Accept', 'X-Requested-With'],
     supports_credentials=False)

# Data loading management
_data_loading_lock = threading.Lock()
_data_loaded = False

def initialize_data():
    """Initialize data loading in background thread with memory optimization"""
    global _data_loaded
    with _data_loading_lock:
        if not _data_loaded:
            print("🚀 Initializing data loading...")
            try:
                # Check if data is already cached to avoid reload
                if cache.is_loaded():
                    print("✅ Data already loaded from cache")
                    _data_loaded = True
                    return
                
                # Load data with timeout protection
                load_data()
                _data_loaded = True
                print("✅ Data initialization completed")
                
                # Force garbage collection after data loading
                import gc
                gc.collect()
                
            except Exception as e:
                print(f"❌ Data initialization failed: {e}")
                # Don't exit, let the app start anyway
                time.sleep(5)  # Wait before potential retry

# Start data loading in background thread
print("🔄 Starting background data initialization...")
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