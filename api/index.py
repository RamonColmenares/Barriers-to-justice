from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from datetime import datetime
import json
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
import requests
import io
import gzip
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['DEBUG'] = False

# Cache for data in memory (will reset on each cold start in Vercel)
_data_cache = {
    'juvenile_cases': None,
    'proceedings': None,
    'reps_assigned': None, 
    'lookup_decisions': None,
    'lookup_juvenile': None,
    'analysis_filtered': None,
    'data_loaded': False
}

# Cache file paths for persistent storage
def get_cache_dir():
    """Get the cache directory path"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    cache_dir = os.path.join(base_path, "cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

CACHE_FILES = {
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
    'juvenile_history_cleaned': '1iRayX8VCZzh8wkLDJAh7rkzP6IrzUThG',
    'tblDecCode': '1BKdS_jJ5gVVO_7Wp1kW1qzGFKd7g_3Hd',
    'tblLookup_Juvenile': '1V8kB0F3hhcvy0h-0qX2D-3dIhBPzMAGs'
}

def load_from_cache():
    """Load processed data from cache files"""
    global _data_cache
    
    try:
        cache_dir = get_cache_dir()
        print("🔍 Checking for cached data...")
        
        # Check if all required cache files exist
        required_caches = ['juvenile_cases', 'proceedings', 'reps_assigned', 'lookup_decisions']
        cache_files_exist = all(
            os.path.exists(os.path.join(cache_dir, CACHE_FILES[key])) 
            for key in required_caches
        )
        
        if not cache_files_exist:
            print("❌ Cache files not found or incomplete")
            return False
            
        print("✅ Loading data from cache...")
        
        # Load each cached dataset
        for key in required_caches:
            cache_file_path = os.path.join(cache_dir, CACHE_FILES[key])
            with open(cache_file_path, 'rb') as f:
                _data_cache[key] = pickle.load(f)
                print(f"   📁 Loaded {key} from cache")
        
        # Load optional lookup_juvenile if it exists
        juvenile_cache_path = os.path.join(cache_dir, CACHE_FILES['lookup_juvenile'])
        if os.path.exists(juvenile_cache_path):
            with open(juvenile_cache_path, 'rb') as f:
                _data_cache['lookup_juvenile'] = pickle.load(f)
                print("   📁 Loaded lookup_juvenile from cache")
        
        # Load analysis data if it exists
        analysis_cache_path = os.path.join(cache_dir, CACHE_FILES['analysis_filtered'])
        if os.path.exists(analysis_cache_path):
            with open(analysis_cache_path, 'rb') as f:
                _data_cache['analysis_filtered'] = pickle.load(f)
                print("   📁 Loaded analysis_filtered from cache")
        
        _data_cache['data_loaded'] = True
        print("🚀 All data loaded from cache successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading from cache: {e}")
        return False

def save_to_cache():
    """Save processed data to cache files"""
    global _data_cache
    
    try:
        cache_dir = get_cache_dir()
        print("💾 Saving data to cache...")
        
        # Save each dataset to cache
        for key, data in _data_cache.items():
            if key != 'data_loaded' and data is not None:
                cache_file_path = os.path.join(cache_dir, CACHE_FILES[key])
                with open(cache_file_path, 'wb') as f:
                    pickle.dump(data, f)
                    print(f"   💾 Saved {key} to cache")
        
        print("✅ Data cached successfully for future use!")
        return True
        
    except Exception as e:
        print(f"❌ Error saving to cache: {e}")
        return False

def download_from_google_drive(file_id, is_gzipped=True):
    """Download a file from Google Drive using its file ID"""
    try:
        print(f"  🌐 Downloading file {file_id}...")
        
        # Try multiple URLs for Google Drive downloads
        urls = [
            f"https://drive.google.com/uc?id={file_id}&export=download",
            f"https://drive.google.com/uc?export=download&id={file_id}",
            f"https://drive.google.com/file/d/{file_id}/view?usp=sharing"
        ]
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        response = None
        for url_attempt, url in enumerate(urls):
            try:
                print(f"    Trying URL {url_attempt + 1}...")
                response = session.get(url, stream=True, timeout=60)
                response.raise_for_status()
                
                # Check if we got HTML instead of file content
                content_type = response.headers.get('content-type', '').lower()
                if 'text/html' in content_type and len(response.content) < 10000:
                    print(f"    Got HTML response, size: {len(response.content)}")
                    continue
                    
                # Valid response found
                break
                
            except Exception as e:
                print(f"    URL {url_attempt + 1} failed: {e}")
                continue
                
        if response is None or 'text/html' in response.headers.get('content-type', '').lower():
            print(f"  ❌ All download attempts failed for {file_id}")
            return None
        
        # Process the file content
        try:
            if is_gzipped:
                # Handle gzipped content
                content = gzip.decompress(response.content)
                print(f"  ✅ Downloaded and decompressed {len(content)} bytes")
                return io.StringIO(content.decode('utf-8'))
            else:
                # Handle plain text content
                print(f"  ✅ Downloaded {len(response.content)} bytes")
                return io.StringIO(response.text)
                
        except gzip.BadGzipFile:
            # File might not be gzipped even if we expected it to be
            print(f"  ⚠️ File {file_id} is not gzipped, trying as plain text...")
            return io.StringIO(response.text)
        except UnicodeDecodeError:
            print(f"  ❌ Unable to decode file {file_id} as text")
            return None
            
    except Exception as e:
        print(f"  ❌ Error downloading file {file_id}: {e}")
        return None

def load_data():
    """Load and process datasets with caching strategy - prioritize real data from Google Drive"""
    global _data_cache
    
    if _data_cache['data_loaded']:
        return True
        
    try:
        # Strategy 1: Try to load from cache first (fastest)
        if load_from_cache():
            # If we have analysis data cached, we're done
            if _data_cache['analysis_filtered'] is not None:
                return True
            # Otherwise, process analysis data
            print("📊 Processing analysis data...")
            process_analysis_data()
            save_to_cache()  # Save the new analysis data
            return True
        
        # Strategy 2: PRIORITIZE Google Drive download to get real data (like notebook)
        print("🌐 Loading real data from Google Drive (like notebook)...")
        if load_data_from_google_drive():
            process_analysis_data()
            save_to_cache()  # Cache the downloaded data
            return True
            
        # Strategy 3: Try to load from local files as backup
        print("📁 Google Drive failed, trying local files...")
        if load_data_from_local_files():
            process_analysis_data()
            save_to_cache()  # Cache the data for next time
            return True
            
        # Strategy 4: Final fallback to sample data (only if everything else fails)
        print("⚠️ All real data sources failed, using fallback sample data...")
        return load_fallback_data()
        
    except Exception as e:
        print(f"❌ Error in load_data: {e}")
        # Don't immediately fallback to sample data - try Google Drive first
        print("🌐 Retrying with Google Drive...")
        try:
            if load_data_from_google_drive():
                process_analysis_data()
                save_to_cache()
                return True
        except:
            pass
        return load_fallback_data()

def load_data_from_google_drive():
    """Load data from Google Drive - EXACTLY like notebook, with fallback to empty data"""
    try:
        print("🌐 Loading real data from Google Drive (matching notebook exactly)...")
        
        # Initialize with empty DataFrames to prevent explosions
        _data_cache['juvenile_cases'] = pd.DataFrame()
        _data_cache['reps_assigned'] = pd.DataFrame() 
        _data_cache['proceedings'] = pd.DataFrame()
        _data_cache['lookup_decisions'] = pd.DataFrame()
        _data_cache['lookup_juvenile'] = pd.DataFrame()
        
        success_count = 0
        
        # Load cases data (EXACTLY like notebook)
        print("📊 Downloading juvenile cases...")
        try:
            cases_file = download_from_google_drive(GOOGLE_DRIVE_FILES['juvenile_cases'], is_gzipped=True)
            if cases_file is not None:
                dtype = {
                    "IDNCASE": "Int64",
                    "NAT": "category",
                    "LANG": "category",
                    "CUSTODY": "category",
                    "CASE_TYPE": "category",
                    "LATEST_CAL_TYPE": "category",
                    "Sex": "category",
                }
                
                parse_dates = [
                    "LATEST_HEARING",
                    "DATE_OF_ENTRY",
                    "C_BIRTHDATE",
                    "DATE_DETAINED",
                    "DATE_RELEASED",
                ]
                
                _data_cache['juvenile_cases'] = pd.read_csv(
                    filepath_or_buffer=cases_file,
                    dtype=dtype,
                    parse_dates=parse_dates,
                    low_memory=False,
                )
                print(f"  ✅ Loaded {len(_data_cache['juvenile_cases']):,} juvenile cases")
                success_count += 1
            else:
                print("  ⚠️ Failed to download juvenile cases, using empty DataFrame")
        except Exception as e:
            print(f"  ❌ Error processing juvenile cases: {e}")
        
        # Load reps_assigned data (EXACTLY like notebook)
        print("📊 Downloading reps assigned...")
        try:
            reps_file = download_from_google_drive(GOOGLE_DRIVE_FILES['juvenile_reps_assigned'], is_gzipped=True)
            if reps_file is not None:
                _data_cache['reps_assigned'] = pd.read_csv(
                    filepath_or_buffer=reps_file,
                    dtype={
                        "IDNREPSASSIGNED": "Int64",
                        "IDNCASE": "int64",
                        "STRATTYLEVEL": "category",
                        "STRATTYTYPE": "category",
                    },
                    low_memory=False,
                )
                
                # Convert reps_assigned date columns to datetime (EXACTLY like notebook)
                if not _data_cache['reps_assigned'].empty:
                    _data_cache['reps_assigned']["E_28_DATE"] = pd.to_datetime(_data_cache['reps_assigned']["E_28_DATE"], errors="coerce")
                    _data_cache['reps_assigned']["E_27_DATE"] = pd.to_datetime(_data_cache['reps_assigned']["E_27_DATE"], errors="coerce")
                
                print(f"  ✅ Loaded {len(_data_cache['reps_assigned']):,} representation assignments")
                success_count += 1
            else:
                print("  ⚠️ Failed to download reps assigned, using empty DataFrame")
        except Exception as e:
            print(f"  ❌ Error processing reps assigned: {e}")
        
        # Load proceedings data (EXACTLY like notebook)
        print("📊 Downloading proceedings...")
        try:
            proceedings_file = download_from_google_drive(GOOGLE_DRIVE_FILES['juvenile_proceedings'], is_gzipped=True)
            if proceedings_file is not None:
                _data_cache['proceedings'] = pd.read_csv(
                    filepath_or_buffer=proceedings_file,
                    dtype={
                        "IDNPROCEEDING": "Int64",
                        "IDNCASE": "Int64",
                        "ABSENTIA": "category",
                        "DEC_CODE": "category",
                    },
                    low_memory=False,
                )
                
                # Convert proceeding date columns to datetime (EXACTLY like notebook)
                if not _data_cache['proceedings'].empty:
                    date_cols = ["OSC_DATE", "INPUT_DATE", "COMP_DATE"]
                    for col in date_cols:
                        if col in _data_cache['proceedings'].columns:
                            _data_cache['proceedings'][col] = pd.to_datetime(_data_cache['proceedings'][col], errors="coerce")
                
                print(f"  ✅ Loaded {len(_data_cache['proceedings']):,} proceedings")
                success_count += 1
            else:
                print("  ⚠️ Failed to download proceedings, using empty DataFrame")
        except Exception as e:
            print(f"  ❌ Error processing proceedings: {e}")
        
        # Load decision code lookup table (EXACTLY like notebook)
        print("📊 Downloading decision codes...")
        try:
            lookup_file = download_from_google_drive(GOOGLE_DRIVE_FILES['tblDecCode'], is_gzipped=False)
            if lookup_file is not None:
                _data_cache['lookup_decisions'] = pd.read_csv(
                    filepath_or_buffer=lookup_file,
                    delimiter="\t",
                    dtype={"strCode": "category"},  # Use strCode not DEC_CODE
                )
                print(f"  ✅ Loaded {len(_data_cache['lookup_decisions'])} decision codes")
                success_count += 1
            else:
                # Use the exact same fallback as notebook
                print("  ⚠️ Using hardcoded decision codes (like notebook fallback)...")
                _data_cache['lookup_decisions'] = pd.DataFrame({
                    'strCode': ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W'],
                    'strDescription': [
                        'Asylum Granted', 'Continued', 'Granted Relief', 'Relief Granted', 
                        'Special Immigration Juvenile Status', 'Terminated Favorably',
                        'Denied', 'Entry of Appearance', 'Voluntary Departure', 'Dismissed',
                        'Other', 'Withdrawn'
                    ]
                })
                success_count += 1
        except Exception as e:
            print(f"  ❌ Error processing decision codes: {e}")
            # Fallback to hardcoded decision codes
            _data_cache['lookup_decisions'] = pd.DataFrame({
                'strCode': ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W'],
                'strDescription': [
                    'Asylum Granted', 'Continued', 'Granted Relief', 'Relief Granted', 
                    'Special Immigration Juvenile Status', 'Terminated Favorably',
                    'Denied', 'Entry of Appearance', 'Voluntary Departure', 'Dismissed',
                    'Other', 'Withdrawn'
                ]
            })
            success_count += 1
        
        # Load juvenile lookup table (optional - EXACTLY like notebook)
        print("📊 Downloading juvenile lookup...")
        try:
            juvenile_lookup_file = download_from_google_drive(GOOGLE_DRIVE_FILES['tblLookup_Juvenile'], is_gzipped=False)
            if juvenile_lookup_file is not None:
                _data_cache['lookup_juvenile'] = pd.read_csv(
                    filepath_or_buffer=juvenile_lookup_file,
                    delimiter="\t",
                    dtype={"idnJuvenile": "category"},
                )
                print(f"  ✅ Loaded {len(_data_cache['lookup_juvenile'])} juvenile lookup entries")
            else:
                print("  ⚠️ Juvenile lookup file not loaded (optional)")
                _data_cache['lookup_juvenile'] = pd.DataFrame()
        except Exception as e:
            print(f"  ❌ Error processing juvenile lookup: {e}")
            _data_cache['lookup_juvenile'] = pd.DataFrame()
        
        # Check if we have enough data to proceed
        if success_count >= 3:  # We need at least cases, proceedings, and lookup_decisions
            _data_cache['data_loaded'] = True
            print(f"🚀 Google Drive data loaded successfully! ({success_count}/4 files)")
        else:
            print(f"⚠️ Only {success_count}/4 required files loaded - using empty data")
            _data_cache['data_loaded'] = True  # Still mark as loaded to prevent infinite loops
        
        # Print summary like notebook
        print(f"📈 Data Summary:")
        print(f"   Cases: {len(_data_cache['juvenile_cases']):,}")
        print(f"   Proceedings: {len(_data_cache['proceedings']):,}")
        print(f"   Representations: {len(_data_cache['reps_assigned']):,}")
        print(f"   Decision codes: {len(_data_cache['lookup_decisions'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading from Google Drive: {e}")
        import traceback
        traceback.print_exc()
        
        # Initialize empty DataFrames to prevent explosions
        _data_cache['juvenile_cases'] = pd.DataFrame()
        _data_cache['reps_assigned'] = pd.DataFrame() 
        _data_cache['proceedings'] = pd.DataFrame()
        _data_cache['lookup_decisions'] = pd.DataFrame({
            'strCode': ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W'],
            'strDescription': [
                'Asylum Granted', 'Continued', 'Granted Relief', 'Relief Granted', 
                'Special Immigration Juvenile Status', 'Terminated Favorably',
                'Denied', 'Entry of Appearance', 'Voluntary Departure', 'Dismissed',
                'Other', 'Withdrawn'
            ]
        })
        _data_cache['lookup_juvenile'] = pd.DataFrame()
        _data_cache['data_loaded'] = True
        
        return True  # Return True to prevent fallback to sample data

def load_data_from_local_files():
    """Load data from local files (original method)"""
    global _data_cache
    
    try:
        print("Loading compressed datasets from local files...")
        
        # Define paths to data files (in the api/data directory)
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, "data")
        
        # Check if data directory exists
        if not os.path.exists(data_path):
            print(f"Data directory not found: {data_path}")
            # In production, try alternative paths
            possible_paths = [
                "/tmp/data",  # Vercel temp directory
                os.path.join(os.getcwd(), "data"),  # Current working directory
                "/var/task/data"  # Lambda/Vercel task directory
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    data_path = path
                    print(f"Using data path: {data_path}")
                    break
            else:
                print("No data directory found. Using fallback data.")
                return load_fallback_data()
        
        cases_path = os.path.join(data_path, "juvenile_cases_cleaned.csv.gz")
        proceedings_path = os.path.join(data_path, "juvenile_proceedings_cleaned.csv.gz")
        reps_assigned_path = os.path.join(data_path, "juvenile_reps_assigned.csv.gz")
        lookup_decision_path = os.path.join(data_path, "tblDecCode.csv")
        lookup_juvenile_path = os.path.join(data_path, "tblLookup_Juvenile.csv")
        
        # Check if files exist
        required_files = [cases_path, proceedings_path, reps_assigned_path, lookup_decision_path]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"Missing data files: {missing_files}")
            return load_fallback_data()
        
        # Load cases data with proper dtypes and date parsing
        dtype = {
            "IDNCASE": "Int64",
            "NAT": "category",
            "LANG": "category",
            "CUSTODY": "category",
            "CASE_TYPE": "category",
            "LATEST_CAL_TYPE": "category",
            "Sex": "category",
        }
        
        parse_dates = [
            "LATEST_HEARING",
            "DATE_OF_ENTRY",
            "C_BIRTHDATE",
            "DATE_DETAINED",
            "DATE_RELEASED",
        ]
        
        _data_cache['juvenile_cases'] = pd.read_csv(
            filepath_or_buffer=cases_path,
            dtype=dtype,
            parse_dates=parse_dates,
            low_memory=False,
        )
        
        # Load reps_assigned data
        _data_cache['reps_assigned'] = pd.read_csv(
            filepath_or_buffer=reps_assigned_path,
            dtype={
                "IDNREPSASSIGNED": "Int64",
                "IDNCASE": "int64",
                "STRATTYLEVEL": "category",
                "STRATTYTYPE": "category",
            },
            compression="gzip",
            low_memory=False,
        )
        
        # Convert reps_assigned date columns to datetime
        _data_cache['reps_assigned']["E_28_DATE"] = pd.to_datetime(_data_cache['reps_assigned']["E_28_DATE"], errors="coerce")
        _data_cache['reps_assigned']["E_27_DATE"] = pd.to_datetime(_data_cache['reps_assigned']["E_27_DATE"], errors="coerce")
        
        # Load proceedings data
        _data_cache['proceedings'] = pd.read_csv(
            filepath_or_buffer=proceedings_path,
            dtype={
                "IDNPROCEEDING": "Int64",
                "IDNCASE": "Int64",
                "ABSENTIA": "category",
                "DEC_CODE": "category",
            },
            low_memory=False,
        )
        
        # Convert proceeding date columns to datetime
        date_cols = ["OSC_DATE", "INPUT_DATE", "COMP_DATE"]
        for col in date_cols:
            if col in _data_cache['proceedings'].columns:
                _data_cache['proceedings'][col] = pd.to_datetime(_data_cache['proceedings'][col], errors="coerce")
        
        # Load decision code lookup table
        _data_cache['lookup_decisions'] = pd.read_csv(
            filepath_or_buffer=lookup_decision_path,
            delimiter="\t",
            dtype={"DEC_CODE": "category"},
        )
        
        # Load juvenile lookup table (optional)
        if os.path.exists(lookup_juvenile_path):
            _data_cache['lookup_juvenile'] = pd.read_csv(
                filepath_or_buffer=lookup_juvenile_path,
                delimiter="\t",
                dtype={"idnJuvenile": "category"},
            )
        else:
            print("Juvenile lookup file not found (optional)")
            _data_cache['lookup_juvenile'] = None
        
        _data_cache['data_loaded'] = True
        print("✅ Data loaded successfully from local files!")
        return True
        
    except Exception as e:
        print(f"Error loading from local files: {str(e)}")
        print("Falling back to sample data...")
        return load_fallback_data()

def load_fallback_data():
    """Load fallback sample data when real datasets are not available (for Vercel deployment)"""
    global _data_cache
    
    try:
        print("Loading fallback sample data...")
        
        # Create sample data that mimics the real structure
        sample_size = 1000
        
        # Sample cases data
        _data_cache['juvenile_cases'] = pd.DataFrame({
            'IDNCASE': range(1, sample_size + 1),
            'NAT': np.random.choice(['Mexico', 'Guatemala', 'El Salvador', 'Honduras', 'Other'], sample_size),
            'LANG': np.random.choice(['Spanish', 'English', 'Other'], sample_size),
            'CUSTODY': np.random.choice(['Released', 'Detained'], sample_size),
            'CASE_TYPE': np.random.choice(['Removal', 'Asylum', 'Other'], sample_size),
            'Sex': np.random.choice(['M', 'F'], sample_size),
            'LATEST_HEARING': pd.date_range('2018-01-01', '2025-01-01', periods=sample_size),
            'C_BIRTHDATE': pd.date_range('2005-01-01', '2015-01-01', periods=sample_size)
        })
        
        # Sample representation data with correct structure
        rep_cases = np.random.choice(range(1, sample_size + 1), sample_size // 2, replace=False)
        _data_cache['reps_assigned'] = pd.DataFrame({
            'IDNCASE': rep_cases,
            'STRATTYLEVEL': np.random.choice(['COURT', 'BOARD', 'A', 'B'], len(rep_cases)),
            'STRATTYTYPE': np.random.choice(['Pro Bono', 'Legal Aid', 'Private'], len(rep_cases))
        })
        
        # Sample proceedings data with correct decision codes from notebook
        decision_codes = ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W']
        _data_cache['proceedings'] = pd.DataFrame({
            'IDNCASE': range(1, sample_size + 1),
            'DEC_CODE': np.random.choice(decision_codes, sample_size),
            'COMP_DATE': pd.date_range('2018-01-01', '2025-01-01', periods=sample_size),
            'NAT': np.random.choice(['Mexico', 'Guatemala', 'El Salvador', 'Honduras'], sample_size),
            'LANG': np.random.choice(['Spanish', 'English'], sample_size),
            'CASE_TYPE': np.random.choice(['Removal', 'Asylum'], sample_size)
        })
        
        # Sample lookup data with correct structure from notebook
        _data_cache['lookup_decisions'] = pd.DataFrame({
            'strCode': ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W'],
            'strDescription': [
                'Asylum Granted', 'Continued', 'Granted Relief', 'Relief Granted', 
                'Special Immigration Juvenile Status', 'Terminated Favorably',
                'Denied', 'Entry of Appearance', 'Voluntary Departure', 'Dismissed',
                'Other', 'Withdrawn'
            ]
        })
        
        # Sample juvenile lookup data (optional)
        _data_cache['lookup_juvenile'] = pd.DataFrame({
            'idnJuvenile': ['JUV001', 'JUV002', 'JUV003'],
            'strDescription': ['Category 1', 'Category 2', 'Category 3']
        })
        
        _data_cache['data_loaded'] = True
        print("✅ Fallback data loaded successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading fallback data: {str(e)}")
        return False

def process_analysis_data():
    """Process data for analysis exactly like in the notebook - handle empty data gracefully"""
    global _data_cache
    
    try:
        if (_data_cache['juvenile_cases'] is None or 
            _data_cache['proceedings'] is None or 
            _data_cache['reps_assigned'] is None or
            _data_cache['lookup_decisions'] is None):
            print("❌ Cannot process analysis data - missing datasets")
            return False
        
        # Check if we have empty DataFrames
        if (_data_cache['juvenile_cases'].empty or 
            _data_cache['proceedings'].empty or 
            _data_cache['lookup_decisions'].empty):
            print("⚠️ Processing empty datasets - creating minimal analysis structure")
            
            # Create minimal empty analysis_filtered
            _data_cache['analysis_filtered'] = pd.DataFrame(columns=[
                'IDNCASE', 'HAS_LEGAL_REP', 'BINARY_OUTCOME', 'POLICY_ERA', 
                'REPRESENTATION_LEVEL', 'DEC_CODE', 'decision_description',
                'COMP_DATE', 'LATEST_HEARING', 'hearing_date_combined'
            ])
            
            print("✅ Empty analysis data structure created")
            return True
            
        print("Processing analysis data exactly like notebook...")
        
        # Step 1: Merge proceedings with decision descriptions (EXACTLY like notebook)
        proceedings_with_decisions = _data_cache['proceedings'][
            ['IDNCASE', 'COMP_DATE', 'NAT', 'LANG', 'CASE_TYPE', 'DEC_CODE']
        ].merge(
            _data_cache['lookup_decisions'][['strCode', 'strDescription']],  # Use strCode from lookup table
            how='left',
            left_on='DEC_CODE',  # Column in proceedings table
            right_on='strCode'   # Column in lookup table
        )
        
        # Drop strCode and rename strDescription (EXACTLY like notebook)
        proceedings_with_decisions = proceedings_with_decisions.drop(columns=['strCode'])
        proceedings_with_decisions = proceedings_with_decisions.rename(
            columns={'strDescription': 'decision_description'}
        )
        
        # Step 2: Merge juvenile_cases with proceedings_with_decisions (EXACTLY like notebook)
        merged_data = _data_cache['juvenile_cases'][
            ['IDNCASE', 'NAT', 'LANG', 'CASE_TYPE', 'Sex', 'C_BIRTHDATE', 'LATEST_HEARING']
        ].merge(
            proceedings_with_decisions[['IDNCASE', 'COMP_DATE', 'DEC_CODE', 'decision_description']],
            left_on='IDNCASE',
            right_on='IDNCASE',
            how='left'
        )
        
        # Step 3: Merge with reps_assigned (EXACTLY like notebook)
        if not _data_cache['reps_assigned'].empty:
            merged_data = merged_data.merge(
                _data_cache['reps_assigned'][['IDNCASE', 'STRATTYLEVEL']], 
                on='IDNCASE', 
                how='left'
            )
        else:
            # Add empty STRATTYLEVEL column if reps_assigned is empty
            merged_data['STRATTYLEVEL'] = pd.Categorical([])
        
        # Step 4: Fill missing STRATTYLEVEL values EXACTLY like notebook
        if 'STRATTYLEVEL' in merged_data.columns:
            # Convert to categorical if not already
            if not pd.api.types.is_categorical_dtype(merged_data['STRATTYLEVEL']):
                merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].astype('category')
            
            merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].cat.add_categories(['no_representation'])
            merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].fillna('no_representation')
        else:
            merged_data['STRATTYLEVEL'] = pd.Categorical(['no_representation'] * len(merged_data))
        
        # Rename to REPRESENTATION_LEVEL (EXACTLY like notebook)
        merged_data = merged_data.rename(columns={'STRATTYLEVEL': 'REPRESENTATION_LEVEL'})
        
        # Step 5: Create hearing_date_combined EXACTLY like notebook
        if 'COMP_DATE' in merged_data.columns:
            if merged_data['COMP_DATE'].dtype == 'object':
                merged_data['COMP_DATE'] = pd.to_datetime(merged_data['COMP_DATE'], errors='coerce')
        else:
            merged_data['COMP_DATE'] = pd.NaT
            
        if 'LATEST_HEARING' in merged_data.columns:
            if merged_data['LATEST_HEARING'].dtype == 'object':
                merged_data['LATEST_HEARING'] = pd.to_datetime(merged_data['LATEST_HEARING'], errors='coerce')
        else:
            merged_data['LATEST_HEARING'] = pd.NaT
            
        merged_data['hearing_date_combined'] = merged_data['COMP_DATE'].fillna(merged_data['LATEST_HEARING'])
        
        # Step 6: Determine policy era EXACTLY like notebook
        def determine_policy_era(date):
            if pd.isna(date):
                return "other"
            if date.year >= 2018 and date.year < 2021:
                return "Trump Era I (2018-2020)"
            elif date.year >= 2021 and date.year < 2025:
                return "Biden Era (2021-2024)"
            elif date.year >= 2025 and date <= pd.Timestamp.now():
                return "Trump Era II (2025-)"
            else:
                return "other"
        
        merged_data['POLICY_ERA'] = merged_data['hearing_date_combined'].apply(determine_policy_era)
        
        # Step 7: Create legal representation indicator EXACTLY like notebook
        merged_data['HAS_LEGAL_REP'] = merged_data['REPRESENTATION_LEVEL'].apply(
            lambda x: "No Legal Representation"
            if x == "no_representation"
            else ("Has Legal Representation" if x == "COURT" or x == "BOARD" else "Unknown")
        )
        
        # Step 8: Create binary outcome classification EXACTLY like notebook
        favorable_decisions = ["A", "C", "G", "R", "S", "T"]  # EXACTLY from notebook
        unfavorable_decisions = ["D", "E", "V", "X"]  # EXACTLY from notebook
        other_decisions = ["O", "W"]  # EXACTLY from notebook
        
        def categorize_outcome(DEC_CODE):
            if pd.isna(DEC_CODE):
                return "Unknown"
            elif DEC_CODE in favorable_decisions:
                return "Favorable" 
            elif DEC_CODE in unfavorable_decisions:
                return "Unfavorable"
            else:
                return "Other"
        
        merged_data['BINARY_OUTCOME'] = merged_data['DEC_CODE'].apply(categorize_outcome)
        merged_data['CASE_OUTCOME'] = merged_data.get('decision_description', '')
        
        # Step 9: Create analysis_filtered EXACTLY like notebook
        analysis_filtered = merged_data[
            (merged_data['HAS_LEGAL_REP'] != "Unknown") &
            (merged_data['BINARY_OUTCOME'] != "Unknown") &
            (merged_data['BINARY_OUTCOME'] != "Other")
        ].copy()
        
        # Store processed data
        _data_cache['merged_data'] = merged_data
        _data_cache['analysis_filtered'] = analysis_filtered
        
        print(f"Analysis data processed successfully!")
        print(f"Total merged records: {len(merged_data):,}")
        print(f"Filtered analysis records: {len(analysis_filtered):,}")
        
        if not analysis_filtered.empty:
            print(f"Legal representation distribution: {analysis_filtered['HAS_LEGAL_REP'].value_counts().to_dict()}")
            print(f"Outcome distribution: {analysis_filtered['BINARY_OUTCOME'].value_counts().to_dict()}")
        else:
            print("No filtered analysis records available")
        
        return True
        
    except Exception as e:
        print(f"Error processing analysis data: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Create minimal empty analysis_filtered to prevent explosions
        _data_cache['analysis_filtered'] = pd.DataFrame(columns=[
            'IDNCASE', 'HAS_LEGAL_REP', 'BINARY_OUTCOME', 'POLICY_ERA', 
            'REPRESENTATION_LEVEL', 'DEC_CODE', 'decision_description',
            'COMP_DATE', 'LATEST_HEARING', 'hearing_date_combined'
        ])
        
        return True  # Return True to prevent further explosions

def get_data_statistics():
    """Calculate real statistics from the loaded data"""
    if not _data_cache['data_loaded'] or _data_cache['juvenile_cases'] is None:
        return None
    
    try:
        # Calculate basic statistics
        total_cases = len(_data_cache['juvenile_cases'])
        
        # Nationality distribution
        nat_counts = _data_cache['juvenile_cases']['NAT'].value_counts().head(10).to_dict()
        
        # Language distribution  
        lang_counts = _data_cache['juvenile_cases']['LANG'].value_counts().to_dict()
        
        # Custody distribution
        custody_counts = _data_cache['juvenile_cases']['CUSTODY'].value_counts().to_dict()
        
        # Case type distribution
        case_type_counts = _data_cache['juvenile_cases']['CASE_TYPE'].value_counts().to_dict()
        
        # Gender distribution
        gender_counts = _data_cache['juvenile_cases']['Sex'].value_counts().to_dict()
        
        # Calculate representation statistics
        rep_stats = {}
        if _data_cache['reps_assigned'] is not None:
            # Merge with reps data to get representation info
            cases_with_rep = _data_cache['juvenile_cases'].merge(_data_cache['reps_assigned'], on='IDNCASE', how='left')
            has_representation = (~cases_with_rep['STRATTYLEVEL'].isna()).sum()
            rep_rate = (has_representation / total_cases) * 100 if total_cases > 0 else 0
            
            # Attorney type distribution
            atty_type_counts = cases_with_rep['STRATTYTYPE'].value_counts().to_dict()
            rep_stats = {
                'representation_rate': round(rep_rate, 1),
                'attorney_types': atty_type_counts
            }
        
        # Calculate average age if birth date is available
        avg_age = None
        if 'C_BIRTHDATE' in _data_cache['juvenile_cases'].columns:
            current_date = pd.Timestamp.now()
            ages = (current_date - _data_cache['juvenile_cases']['C_BIRTHDATE']).dt.days / 365.25
            avg_age = ages.mean() if not ages.isna().all() else None
        
        return {
            'total_cases': total_cases,
            'average_age': round(avg_age, 1) if avg_age else None,
            'nationalities': nat_counts,
            'languages': lang_counts,
            'custody': custody_counts,
            'case_types': case_type_counts,
            'gender': gender_counts,
            **rep_stats
        }
        
    except Exception as e:
        print(f"Error calculating statistics: {str(e)}")
        return None

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "juvenile-immigration-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

@app.route('/api/overview')
def get_overview():
    """Get overview statistics from real data"""
    try:
        # Load data if not already loaded
        if not load_data():
            return jsonify({"error": "Failed to load data"}), 500
        
        # Get real statistics from the data
        stats = get_data_statistics()
        if stats is None:
            return jsonify({"error": "Failed to calculate statistics"}), 500
        
        # Calculate time series trends if we have date data
        trends = {}
        if _data_cache['juvenile_cases'] is not None and 'LATEST_HEARING' in _data_cache['juvenile_cases'].columns:
            try:
                # Group by month for trends
                monthly_data = _data_cache['juvenile_cases'].copy()
                monthly_data['month'] = monthly_data['LATEST_HEARING'].dt.to_period('M')
                monthly_counts = monthly_data.groupby('month').size()
                
                # Convert to dictionary for JSON serialization
                trends = {
                    "monthly_cases": {
                        str(month): count for month, count in monthly_counts.tail(12).items()
                    }
                }
            except Exception as e:
                print(f"Error calculating trends: {str(e)}")
                trends = {"monthly_cases": {}}
        
        # Structure the response to match frontend expectations
        overview_data = {
            "total_cases": stats['total_cases'],
            "average_age": stats.get('average_age'),
            "representation_rate": stats.get('representation_rate', 0),
            "top_nationalities": stats['nationalities'],
            "demographic_breakdown": {
                "by_gender": stats['gender'],
                "by_custody": stats['custody'],
                "by_case_type": stats['case_types']
            },
            "representation_breakdown": stats.get('attorney_types', {}),
            "language_breakdown": stats['languages'],
            "trends": trends
        }
        
        return jsonify(overview_data)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/load-data')
def load_data_endpoint():
    """Endpoint to trigger data loading"""
    try:
        success = load_data()
        if success:
            return jsonify({
                "status": "success",
                "message": "Data loaded successfully",
                "cases_count": len(_data_cache['juvenile_cases']) if _data_cache['juvenile_cases'] is not None else 0,
                "proceedings_count": len(_data_cache['proceedings']) if _data_cache['proceedings'] is not None else 0,
                "reps_count": len(_data_cache['reps_assigned']) if _data_cache['reps_assigned'] is not None else 0,
                "data_source": "Google Drive" if _data_cache['juvenile_cases'] is not None and len(_data_cache['juvenile_cases']) > 10000 else "Sample Data"
            })
        else:
            return jsonify({"error": "Failed to load data"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/force-reload-data')
def force_reload_data():
    """Force reload data from Google Drive (clear cache first)"""
    try:
        # Clear cache
        global _data_cache
        _data_cache = {
            'juvenile_cases': None,
            'proceedings': None,
            'reps_assigned': None, 
            'lookup_decisions': None,
            'lookup_juvenile': None,
            'analysis_filtered': None,
            'data_loaded': False
        }
        
        # Force load from Google Drive
        success = load_data_from_google_drive()
        if success:
            process_analysis_data()
            save_to_cache()
            return jsonify({
                "status": "success",
                "message": "Data force-reloaded from Google Drive",
                "cases_count": len(_data_cache['juvenile_cases']) if _data_cache['juvenile_cases'] is not None else 0,
                "proceedings_count": len(_data_cache['proceedings']) if _data_cache['proceedings'] is not None else 0,
                "reps_count": len(_data_cache['reps_assigned']) if _data_cache['reps_assigned'] is not None else 0,
                "analysis_count": len(_data_cache['analysis_filtered']) if _data_cache['analysis_filtered'] is not None else 0
            })
        else:
            return jsonify({"error": "Failed to reload data from Google Drive"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/data-status')
def data_status():
    """Check if data is loaded and get basic info"""
    try:
        return jsonify({
            "data_loaded": _data_cache['data_loaded'],
            "cases_loaded": _data_cache['juvenile_cases'] is not None,
            "proceedings_loaded": _data_cache['proceedings'] is not None,
            "reps_loaded": _data_cache['reps_assigned'] is not None,
            "lookup_loaded": _data_cache['lookup_decisions'] is not None,
            "lookup_juvenile_loaded": _data_cache['lookup_juvenile'] is not None,
            "cases_count": len(_data_cache['juvenile_cases']) if _data_cache['juvenile_cases'] is not None else 0,
            "proceedings_count": len(_data_cache['proceedings']) if _data_cache['proceedings'] is not None else 0,
            "reps_count": len(_data_cache['reps_assigned']) if _data_cache['reps_assigned'] is not None else 0
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/representation-outcomes')
def representation_outcomes():
    """Generate Plotly chart data for representation vs outcomes chart (EXACTLY like notebook)"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # EXACTLY like notebook: Create crosstab for representation vs outcomes
        crosstab = pd.crosstab(
            _data_cache['analysis_filtered']['HAS_LEGAL_REP'], 
            _data_cache['analysis_filtered']['BINARY_OUTCOME']
        )
        
        # EXACTLY like notebook: Calculate percentages using normalize='index' 
        # This gives percentages PER ROW (each representation category sums to 100%)
        percentage_data = pd.crosstab(
            _data_cache['analysis_filtered']['HAS_LEGAL_REP'],
            _data_cache['analysis_filtered']['BINARY_OUTCOME'], 
            normalize='index'  # EXACTLY like notebook - normalize by rows
        ) * 100
        
        # Create Plotly figure exactly like notebook
        fig = go.Figure()
        
        # Add Favorable outcomes bar (using the percentage data from notebook logic)
        fig.add_trace(go.Bar(
            name='Favorable',
            x=crosstab.index,
            y=crosstab['Favorable'],
            marker_color='#10B981',
            text=[f"{p:.1f}%" for p in percentage_data['Favorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Add Unfavorable outcomes bar
        fig.add_trace(go.Bar(
            name='Unfavorable',
            x=crosstab.index,
            y=crosstab['Unfavorable'],
            marker_color='#EF4444',
            text=[f"{p:.1f}%" for p in percentage_data['Unfavorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Update layout to match notebook style
        fig.update_layout(
            title={
                'text': 'Case Outcomes by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            barmode='stack',
            xaxis={
                'title': 'Legal Representation',
                'tickangle': 0,
                'title_font': {'size': 14}
            },
            yaxis={
                'title': 'Count',
                'type': 'log',  # Log scale exactly like in notebook
                'title_font': {'size': 14}
            },
            showlegend=True,
            legend=dict(
                title='Case Outcome',
                orientation='v',
                x=1.05,
                y=1
            ),
            margin=dict(t=60, l=60, r=30, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif'),
            width=800,
            height=500
        )
        
        # Convert to JSON format for frontend
        chart_data = {
            'data': fig.data,
            'layout': fig.layout,
            'config': {
                'responsive': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'displaylogo': False
            }
        }
        
        # Convert to JSON-serializable format
        import plotly.utils
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/time-series')
def time_series_analysis():
    """Generate Plotly time series chart exactly like notebook"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Filter data with valid dates from 2016 onwards (like notebook)
        date_valid = ~_data_cache['analysis_filtered']['LATEST_HEARING'].isna()
        time_series_df = _data_cache['analysis_filtered'][date_valid].copy()
        
        start_date = pd.Timestamp("2016-01-01")
        current_date = pd.Timestamp.now()
        recent_data = time_series_df[
            (time_series_df['LATEST_HEARING'] >= start_date) & 
            (time_series_df['LATEST_HEARING'] <= current_date)
        ]
        
        # Create quarterly data (like notebook)
        recent_data['YEAR_QUARTER'] = recent_data['LATEST_HEARING'].dt.to_period('Q')
        
        quarterly_rep = recent_data.groupby('YEAR_QUARTER').agg(
            total_cases=('HAS_LEGAL_REP', 'count'),
            represented_cases=('HAS_LEGAL_REP', lambda x: (x == 'Has Legal Representation').sum())
        )
        quarterly_rep['representation_rate'] = quarterly_rep['represented_cases'] / quarterly_rep['total_cases']
        
        # Convert to timestamp for plotting
        quarterly_rep['date'] = quarterly_rep.index.to_timestamp()
        
        # Create Plotly figure exactly like notebook
        fig = go.Figure()
        
        # Add main time series line (like notebook)
        fig.add_trace(go.Scatter(
            x=quarterly_rep['date'],
            y=quarterly_rep['representation_rate'],
            mode='lines+markers',
            name='Representation Rate',
            line=dict(color='navy', width=2),
            marker=dict(size=6, color='navy'),
            opacity=0.7
        ))
        
        # Add administration change lines (like notebook)
        admin_changes = [
            (pd.Timestamp("2017-01-20"), "Trump Administration"),
            (pd.Timestamp("2021-01-20"), "Biden Administration"),
            (pd.Timestamp("2025-01-20"), "Trump Administration II")
        ]
        
        shapes = []
        annotations = []
        
        for date, label in admin_changes:
            # Add vertical line
            shapes.append(dict(
                type="line",
                x0=date, x1=date,
                y0=0, y1=1,
                line=dict(color="red", dash="dash", width=2),
                opacity=0.6
            ))
            
            # Add label annotation
            annotations.append(dict(
                x=date,
                y=0.95,
                text=label,
                showarrow=False,
                textangle=-90,
                xanchor="right",
                yanchor="top",
                font=dict(size=10, color="red")
            ))
        
        # Update layout to match notebook exactly
        fig.update_layout(
            title={
                'text': 'Legal Representation Rate for Juvenile Immigration Cases (2016-2025)',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            xaxis={
                'title': 'Year',
                'title_font': {'size': 14},
                'tickformat': '%Y',
                'dtick': 'M12'  # Show every year
            },
            yaxis={
                'title': 'Representation Rate',
                'title_font': {'size': 14},
                'range': [0, 1],
                'tickformat': '.0%'
            },
            shapes=shapes,
            annotations=annotations,
            showlegend=False,
            margin=dict(t=60, l=60, r=30, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif'),
            width=1000,
            height=500
        )
        
        # Add grid (like notebook)
        
        # Convert to JSON format
        chart_data = {
            'data': fig.data,
            'layout': fig.layout,
            'config': {
                'responsive': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'displaylogo': False
            }
        }
        
        import plotly.utils
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/chi-square')
def chi_square_analysis():
    """Generate chi-square analysis results (like notebook) - handle empty data gracefully"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Check if we have empty analysis data
        if _data_cache['analysis_filtered'].empty:
            return jsonify({
                "message": "No analysis data available",
                "representation_by_era": {
                    'chi_square': 0.0,
                    'p_value': 1.0,
                    'degrees_of_freedom': 0,
                    'cramer_v': 0.0,
                    'significant': False,
                    'contingency_table': {}
                },
                "outcomes_by_representation": {
                    'chi_square': 0.0,
                    'p_value': 1.0,
                    'degrees_of_freedom': 0,
                    'cramer_v': 0.0,
                    'significant': False,
                    'odds_ratio': 0.0,
                    'contingency_table': {},
                    'percentages': {
                        'data': {},
                        'with_representation': {'favorable': 0, 'unfavorable': 0},
                        'without_representation': {'favorable': 0, 'unfavorable': 0}
                    }
                }
            })
        
        results = {}
        
        # Chi-square test for representation by policy era
        try:
            era_rep_table = pd.crosstab(
                _data_cache['analysis_filtered']['POLICY_ERA'], 
                _data_cache['analysis_filtered']['HAS_LEGAL_REP']
            )
            
            if era_rep_table.empty or era_rep_table.values.sum() == 0:
                results['representation_by_era'] = {
                    'chi_square': 0.0,
                    'p_value': 1.0,
                    'degrees_of_freedom': 0,
                    'cramer_v': 0.0,
                    'significant': False,
                    'contingency_table': {}
                }
            else:
                chi2_era, p_era, dof_era, _ = stats.chi2_contingency(era_rep_table)
                n_era = era_rep_table.values.sum()
                cramer_v_era = np.sqrt(chi2_era / (n_era * (min(era_rep_table.shape) - 1))) if n_era > 0 and min(era_rep_table.shape) > 1 else 0
                
                results['representation_by_era'] = {
                    'chi_square': round(float(chi2_era), 2),
                    'p_value': float(p_era),
                    'degrees_of_freedom': int(dof_era),
                    'cramer_v': round(float(cramer_v_era), 3),
                    'significant': bool(p_era < 0.05),
                    'contingency_table': era_rep_table.to_dict()
                }
        except Exception as e:
            print(f"Error in era analysis: {e}")
            results['representation_by_era'] = {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'contingency_table': {}
            }
        
        # Chi-square test for outcomes by representation (EXACTLY like notebook)
        try:
            outcome_rep_table = pd.crosstab(
                _data_cache['analysis_filtered']['HAS_LEGAL_REP'],  # Put representation as index (rows)
                _data_cache['analysis_filtered']['BINARY_OUTCOME']   # Put outcome as columns
            )
            
            if outcome_rep_table.empty or outcome_rep_table.values.sum() == 0:
                results['outcomes_by_representation'] = {
                    'chi_square': 0.0,
                    'p_value': 1.0,
                    'degrees_of_freedom': 0,
                    'cramer_v': 0.0,
                    'significant': False,
                    'odds_ratio': 0.0,
                    'contingency_table': {},
                    'percentages': {
                        'data': {},
                        'with_representation': {'favorable': 0, 'unfavorable': 0},
                        'without_representation': {'favorable': 0, 'unfavorable': 0}
                    }
                }
            else:
                chi2_outcome, p_outcome, dof_outcome, _ = stats.chi2_contingency(outcome_rep_table)
                n_outcome = outcome_rep_table.values.sum()
                cramer_v_outcome = np.sqrt(chi2_outcome / (n_outcome * (min(outcome_rep_table.shape) - 1))) if n_outcome > 0 and min(outcome_rep_table.shape) > 1 else 0
                
                # Calculate percentages with normalize='index' (EXACTLY like notebook)
                percentages = pd.crosstab(
                    _data_cache['analysis_filtered']['HAS_LEGAL_REP'],
                    _data_cache['analysis_filtered']['BINARY_OUTCOME'],
                    normalize='index'  # Each representation category sums to 100%
                ) * 100
                
                # Calculate odds ratio (EXACTLY like notebook)
                odds_ratio = 0.0
                try:
                    # Get the actual representation categories from the table
                    rep_categories = outcome_rep_table.index.tolist()
                    outcome_categories = outcome_rep_table.columns.tolist()
                    
                    # Find categories that contain "Has" or "With" for representation
                    with_rep_cat = None
                    without_rep_cat = None
                    
                    for cat in rep_categories:
                        if 'Has' in cat or 'With' in cat:
                            with_rep_cat = cat
                        elif 'No' in cat or 'Without' in cat:
                            without_rep_cat = cat
                    
                    # Calculate odds ratio if we have the required categories
                    if (with_rep_cat and without_rep_cat and 
                        'Favorable' in outcome_categories and 'Unfavorable' in outcome_categories):
                        
                        a = outcome_rep_table.loc[with_rep_cat, 'Favorable']
                        b = outcome_rep_table.loc[with_rep_cat, 'Unfavorable'] 
                        c = outcome_rep_table.loc[without_rep_cat, 'Favorable']
                        d = outcome_rep_table.loc[without_rep_cat, 'Unfavorable']
                        
                        odds_with_rep = a / b if b > 0 else 0
                        odds_without_rep = c / d if d > 0 else 0
                        odds_ratio = odds_with_rep / odds_without_rep if odds_without_rep > 0 else 0
                except Exception as e:
                    print(f"Error calculating odds ratio: {e}")
                    odds_ratio = 0.0
                
                # Build percentages data safely
                percentages_data = percentages.round(1).to_dict() if not percentages.empty else {}
                with_rep_data = {'favorable': 0, 'unfavorable': 0}
                without_rep_data = {'favorable': 0, 'unfavorable': 0}
                
                try:
                    # Find the actual representation categories in percentages
                    for cat in percentages.index:
                        if 'Has' in cat or 'With' in cat:
                            with_rep_data = {
                                'favorable': float(percentages.loc[cat, 'Favorable']) if 'Favorable' in percentages.columns else 0,
                                'unfavorable': float(percentages.loc[cat, 'Unfavorable']) if 'Unfavorable' in percentages.columns else 0
                            }
                        elif 'No' in cat or 'Without' in cat:
                            without_rep_data = {
                                'favorable': float(percentages.loc[cat, 'Favorable']) if 'Favorable' in percentages.columns else 0,
                                'unfavorable': float(percentages.loc[cat, 'Unfavorable']) if 'Unfavorable' in percentages.columns else 0
                            }
                except Exception as e:
                    print(f"Error building percentage data: {e}")
                    
                results['outcomes_by_representation'] = {
                    'chi_square': round(float(chi2_outcome), 2),
                    'p_value': float(p_outcome),
                    'degrees_of_freedom': int(dof_outcome),
                    'cramer_v': round(float(cramer_v_outcome), 3),
                    'significant': bool(p_outcome < 0.05),
                    'odds_ratio': round(float(odds_ratio), 3),
                    'contingency_table': outcome_rep_table.to_dict(),
                    'percentages': {
                        'data': percentages_data,
                        'with_representation': with_rep_data,
                        'without_representation': without_rep_data
                    }
                }
        except Exception as e:
            print(f"Error in outcome analysis: {e}")
            results['outcomes_by_representation'] = {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'odds_ratio': 0.0,
                'contingency_table': {},
                'percentages': {
                    'data': {},
                    'with_representation': {'favorable': 0, 'unfavorable': 0},
                    'without_representation': {'favorable': 0, 'unfavorable': 0}
                }
            }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/outcome-percentages')
def outcome_percentages_chart():
    """Generate the percentage breakdown chart EXACTLY like notebook"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Calculate percentages EXACTLY like notebook with normalize='index'
        # This means each row (representation category) sums to 100%
        percentage_data = pd.crosstab(
            _data_cache['analysis_filtered']['HAS_LEGAL_REP'],
            _data_cache['analysis_filtered']['BINARY_OUTCOME'],
            normalize='index'  # EXACTLY like notebook - normalize by rows
        ) * 100
        
        # Create stacked bar chart with percentages (EXACTLY like notebook)
        fig = go.Figure()
        
        # Add Favorable outcomes (using index as x-axis, which is representation categories)
        fig.add_trace(go.Bar(
            name='Favorable',
            x=percentage_data.index,  # Representation categories
            y=percentage_data['Favorable'],  # Percentage values
            marker_color='#10B981',
            text=[f"{p:.1f}%" for p in percentage_data['Favorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Add Unfavorable outcomes  
        fig.add_trace(go.Bar(
            name='Unfavorable',
            x=percentage_data.index,  # Representation categories
            y=percentage_data['Unfavorable'],  # Percentage values
            marker_color='#EF4444',
            text=[f"{p:.1f}%" for p in percentage_data['Unfavorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Update layout to match notebook
        fig.update_layout(
            title={
                'text': 'Case Outcome Percentages by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            barmode='stack',
            xaxis={
                'title': 'Legal Representation',
                'tickangle': 0,
                'title_font': {'size': 14}
            },
            yaxis={
                'title': 'Percentage (%)',
                'title_font': {'size': 14},
                'range': [0, 100]
            },
            showlegend=True,
            legend=dict(
                title='Case Outcome',
                orientation='v',
                x=1.05,
                y=1
            ),
            margin=dict(t=60, l=60, r=30, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif'),
            width=800,
            height=500
        )
        
        # Convert to JSON
        chart_data = {
            'data': fig.data,
            'layout': fig.layout,
            'config': {
                'responsive': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'displaylogo': False
            }
        }
        
        import plotly.utils
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

# Vercel serverless function handler
def handler(request, context):
    """Vercel handler function"""
    with app.app_context():
        return app.full_dispatch_request()

# For local development
if __name__ == '__main__':
    print("🚀 Starting development server...")
    print("🌐 Backend running on http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET /api/health")
    print("   GET /api/overview")
    print("   GET /api/load-data")
    print("   GET /api/data-status")
    print("   GET /api/findings/representation-outcomes")
    print("   GET /api/findings/time-series")
    print("   GET /api/findings/chi-square")
    app.run(debug=True, host='0.0.0.0', port=5000)
