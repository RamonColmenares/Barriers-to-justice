"""
Configuration and constants for the juvenile immigration API
"""
import os

# Flask configuration
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

# Raw data file names (as specified by user)
RAW_DATA_FILES = {
    'juvenile_history': 'juvenile_history_cleaned.csv.gz',
    'juvenile_cases': 'juvenile_cases_cleaned.csv.gz',
    'juvenile_reps_assigned': 'juvenile_reps_assigned.csv.gz',
    'juvenile_proceedings': 'juvenile_proceedings_cleaned.csv.gz',
    'tblLookup_Juvenile': 'tblLookup_Juvenile.csv',
    'tblDecCode': 'tblDecCode.csv'
}

# Cache configuration
CACHE_FILES = {
    'juvenile_history': 'juvenile_history_cache.pkl',
    'juvenile_cases': 'juvenile_cases_cache.pkl',
    'proceedings': 'proceedings_cache.pkl',
    'reps_assigned': 'reps_assigned_cache.pkl',
    'lookup_decisions': 'lookup_decisions_cache.pkl',
    'lookup_juvenile': 'lookup_juvenile_cache.pkl',
    'analysis_filtered': 'analysis_filtered_cache.pkl'
}

# Google Drive file IDs for the datasets
GOOGLE_DRIVE_FILES = {
    'juvenile_cases': '1XXUKEa9QBCBKAoYSvKWQf19NIsEjWPCo',
    'juvenile_proceedings': '1TEAOTFKZrteqrD2u7sb6ilgpiz10hZJC', 
    'juvenile_reps_assigned': '1tZiPOZfgaJOpPwW9kuGqCvMWk2PAUAIO',
    'juvenile_history': '1iRayX8VCZzh8wkLDJAh7rkzP6IrzUThG',
    'tblDecCode': '1BKdS_jJ5gVVO_7Wp1kW1qzGFKd7g_3Hd',
    'tblLookup_Juvenile': '1V8kB0F3hhcvy0h-0qX2D-3dIhBPzMAGs'
}

# Decision code classifications (from notebook)
FAVORABLE_DECISIONS = ["A", "C", "G", "R", "S", "T"]
UNFAVORABLE_DECISIONS = ["D", "E", "V", "X"]
OTHER_DECISIONS = ["O", "W"]

# Date configurations
START_DATE = "2016-01-01"

ADMIN_CHANGES = [
    ("2017-01-20", "Trump Administration"),
    ("2021-01-20", "Biden Administration"),
    ("2025-01-20", "Trump Administration II")
]

def get_cache_dir():
    """Get the cache directory path"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_path, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_data_dir():
    """Get data directory with fallback paths for different environments"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_path, "data")
    
    if os.path.exists(data_path):
        return data_path
    
    # Alternative paths for production environments
    possible_paths = [
        "/tmp/data",  # Vercel temp directory
        os.path.join(os.getcwd(), "data"),  # Current working directory
        "/var/task/data"  # Lambda/Vercel task directory
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    return None
