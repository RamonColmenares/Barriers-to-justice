"""
Data loading functionality for the juvenile immigration API
Only loads real data from cache or Google Drive - no mock data
"""
import pandas as pd
import requests
import io
import gzip
import pickle
import os
import traceback
from datetime import datetime

try:
    from .config import CACHE_FILES, GOOGLE_DRIVE_FILES, RAW_DATA_FILES, get_cache_dir
    from .models import cache
except ImportError:
    from config import CACHE_FILES, GOOGLE_DRIVE_FILES, RAW_DATA_FILES, get_cache_dir
    from models import cache

def check_raw_files_in_cache():
    """Check if raw data files exist in cache directory"""
    cache_dir = get_cache_dir()
    
    # Check for raw data files
    missing_files = []
    existing_files = []
    
    for file_key, filename in RAW_DATA_FILES.items():
        file_path = os.path.join(cache_dir, filename)
        if os.path.exists(file_path):
            existing_files.append(filename)
        else:
            missing_files.append(filename)
    
    print(f"📁 Raw files in cache: {len(existing_files)}/{len(RAW_DATA_FILES)}")
    for file in existing_files:
        print(f"   ✅ {file}")
    for file in missing_files:
        print(f"   ❌ {file}")
    
    return len(missing_files) == 0

def load_raw_files_from_cache():
    """Load data from raw files in cache directory"""
    try:
        cache_dir = get_cache_dir()
        print("📁 Loading data from raw files in cache...")
        
        # Load juvenile_cases_cleaned.csv.gz
        cases_path = os.path.join(cache_dir, RAW_DATA_FILES['juvenile_cases'])
        if os.path.exists(cases_path):
            print("   Loading juvenile cases...")
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
            juvenile_cases = pd.read_csv(
                cases_path, 
                dtype=dtype,
                parse_dates=parse_dates,
                low_memory=False
            )
            cache.set('juvenile_cases', juvenile_cases)
            print(f"   ✅ Loaded {len(juvenile_cases):,} juvenile cases")
        else:
            raise FileNotFoundError(f"Required file not found: {cases_path}")
        
        # Load juvenile_reps_assigned.csv.gz
        reps_path = os.path.join(cache_dir, RAW_DATA_FILES['juvenile_reps_assigned'])
        if os.path.exists(reps_path):
            print("   Loading representation assignments...")
            reps_assigned = pd.read_csv(
                reps_path,
                dtype={
                    "IDNREPSASSIGNED": "Int64",
                    "IDNCASE": "int64",
                    "STRATTYLEVEL": "category",
                    "STRATTYTYPE": "category",
                },
                low_memory=False
            )
            # Convert date columns
            if not reps_assigned.empty:
                reps_assigned["E_28_DATE"] = pd.to_datetime(reps_assigned["E_28_DATE"], errors="coerce")
                reps_assigned["E_27_DATE"] = pd.to_datetime(reps_assigned["E_27_DATE"], errors="coerce")
            cache.set('reps_assigned', reps_assigned)
            print(f"   ✅ Loaded {len(reps_assigned):,} representation assignments")
        else:
            raise FileNotFoundError(f"Required file not found: {reps_path}")
        
        # Load juvenile_proceedings_cleaned.csv.gz
        proceedings_path = os.path.join(cache_dir, RAW_DATA_FILES['juvenile_proceedings'])
        if os.path.exists(proceedings_path):
            print("   Loading proceedings...")
            proceedings = pd.read_csv(
                proceedings_path,
                dtype={
                    "IDNPROCEEDING": "Int64",
                    "IDNCASE": "Int64", 
                    "ABSENTIA": "category",
                    "DEC_CODE": "category",
                },
                low_memory=False
            )
            # Convert date columns
            if not proceedings.empty:
                date_cols = ["OSC_DATE", "INPUT_DATE", "COMP_DATE"]
                for col in date_cols:
                    if col in proceedings.columns:
                        proceedings[col] = pd.to_datetime(proceedings[col], errors="coerce")
            cache.set('proceedings', proceedings)
            print(f"   ✅ Loaded {len(proceedings):,} proceedings")
        else:
            raise FileNotFoundError(f"Required file not found: {proceedings_path}")
        
        # Load tblDecCode.csv
        lookup_decision_path = os.path.join(cache_dir, RAW_DATA_FILES['tblDecCode'])
        if os.path.exists(lookup_decision_path):
            print("   Loading decision codes...")
            lookup_decisions = pd.read_csv(
                lookup_decision_path,
                delimiter="\t",
                dtype={"strCode": "category"}
            )
            cache.set('lookup_decisions', lookup_decisions)
            print(f"   ✅ Loaded {len(lookup_decisions)} decision codes")
        else:
            raise FileNotFoundError(f"Required file not found: {lookup_decision_path}")
        
        # Load tblLookup_Juvenile.csv (optional)
        lookup_juvenile_path = os.path.join(cache_dir, RAW_DATA_FILES['tblLookup_Juvenile'])
        if os.path.exists(lookup_juvenile_path):
            print("   Loading juvenile lookup...")
            lookup_juvenile = pd.read_csv(
                lookup_juvenile_path,
                delimiter="\t",
                dtype={"idnJuvenile": "category"}
            )
            cache.set('lookup_juvenile', lookup_juvenile)
            print(f"   ✅ Loaded {len(lookup_juvenile)} juvenile lookup entries")
        else:
            print("   ⚠️ Optional juvenile lookup file not found")
            cache.set('lookup_juvenile', pd.DataFrame())
        
        cache.set_loaded(True)
        print("🚀 All data loaded from raw files successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading from raw files: {e}")
        return False

def load_from_cache():
    """Load processed data from cache files"""
    try:
        cache_dir = get_cache_dir()
        print("🔍 Checking for cached processed data...")
        
        # Check if all required cache files exist
        required_caches = ['juvenile_cases', 'proceedings', 'reps_assigned', 'lookup_decisions']
        cache_files_exist = all(
            os.path.exists(os.path.join(cache_dir, CACHE_FILES[key])) 
            for key in required_caches
        )
        
        if not cache_files_exist:
            print("❌ Processed cache files not found")
            return False
            
        print("✅ Loading data from processed cache...")
        
        # Load each cached dataset
        for key in required_caches:
            cache_file_path = os.path.join(cache_dir, CACHE_FILES[key])
            with open(cache_file_path, 'rb') as f:
                cache.set(key, pickle.load(f))
                print(f"   📁 Loaded {key} from cache")
        
        # Load optional lookup_juvenile if it exists
        juvenile_cache_path = os.path.join(cache_dir, CACHE_FILES['lookup_juvenile'])
        if os.path.exists(juvenile_cache_path):
            with open(juvenile_cache_path, 'rb') as f:
                cache.set('lookup_juvenile', pickle.load(f))
                print("   📁 Loaded lookup_juvenile from cache")
        
        # Load analysis data if it exists
        analysis_cache_path = os.path.join(cache_dir, CACHE_FILES['analysis_filtered'])
        if os.path.exists(analysis_cache_path):
            with open(analysis_cache_path, 'rb') as f:
                cache.set('analysis_filtered', pickle.load(f))
                print("   📁 Loaded analysis_filtered from cache")
        
        cache.set_loaded(True)
        print("🚀 All data loaded from processed cache successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error loading from processed cache: {e}")
        return False

def save_to_cache():
    """Save processed data to cache files"""
    try:
        cache_dir = get_cache_dir()
        print("💾 Saving data to cache...")
        
        # Save each dataset to cache
        cache_data = cache.get_all()
        for key, data in cache_data.items():
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
        
        # Return the raw content for saving to cache
        print(f"  ✅ Downloaded {len(response.content)} bytes")
        return response.content
            
    except Exception as e:
        print(f"  ❌ Error downloading file {file_id}: {e}")
        return None

def download_raw_files_from_google_drive():
    """Download raw data files from Google Drive and save to cache directory"""
    try:
        cache_dir = get_cache_dir()
        print("🌐 Downloading raw data files from Google Drive...")
        
        downloaded_count = 0
        
        # Download each file and save to cache
        for file_key, filename in RAW_DATA_FILES.items():
            if file_key in GOOGLE_DRIVE_FILES:
                file_id = GOOGLE_DRIVE_FILES[file_key]
                print(f"📊 Downloading {filename}...")
                
                # Determine if file is gzipped based on extension
                is_gzipped = filename.endswith('.gz')
                content = download_from_google_drive(file_id, is_gzipped)
                
                if content is not None:
                    # Save raw file to cache directory
                    file_path = os.path.join(cache_dir, filename)
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    print(f"  ✅ Saved {filename} to cache")
                    downloaded_count += 1
                else:
                    print(f"  ❌ Failed to download {filename}")
            else:
                print(f"  ⚠️ No Google Drive ID found for {filename}")
        
        print(f"📥 Downloaded {downloaded_count}/{len(RAW_DATA_FILES)} files")
        return downloaded_count > 0
        
    except Exception as e:
        print(f"❌ Error downloading files from Google Drive: {e}")
        return False

def load_data():
    """Load and process datasets - only real data, no mock data"""
    if cache.is_loaded():
        return True
        
    try:
        # Strategy 1: Try to load from processed cache first (fastest)
        if load_from_cache():
            # If we have analysis data cached, we're done
            if cache.get('analysis_filtered') is not None:
                return True
            # Otherwise, process analysis data
            print("📊 Processing analysis data...")
            try:
                from .data_processor import process_analysis_data
            except ImportError:
                from data_processor import process_analysis_data
            process_analysis_data()
            save_to_cache()  # Save the new analysis data
            return True
        
        # Strategy 2: Check if raw files exist in cache, if so load them
        if check_raw_files_in_cache():
            print("📁 Raw files found in cache, loading...")
            if load_raw_files_from_cache():
                print("📊 Processing analysis data...")
                try:
                    from .data_processor import process_analysis_data
                except ImportError:
                    from data_processor import process_analysis_data
                process_analysis_data()
                save_to_cache()  # Cache the processed data
                return True
            
        # Strategy 3: Download files from Google Drive and save to cache
        print("🌐 Downloading files from Google Drive...")
        if download_raw_files_from_google_drive():
            if load_raw_files_from_cache():
                print("📊 Processing analysis data...")
                try:
                    from .data_processor import process_analysis_data
                except ImportError:
                    from data_processor import process_analysis_data
                process_analysis_data()
                save_to_cache()  # Cache the data for next time
                return True
        
        # If we get here, all strategies failed
        print("❌ Failed to load any real data - no fallback provided")
        return False
        
    except Exception as e:
        print(f"❌ Error in load_data: {e}")
        traceback.print_exc()
        return False
