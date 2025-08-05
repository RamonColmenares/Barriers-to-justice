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

# Local imports
from .config import CACHE_FILES, GOOGLE_DRIVE_FILES, RAW_DATA_FILES, get_cache_dir
from .models import cache

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
        
        # Load juvenile_history_cleaned.csv.gz (EXACTLY like notebook)
        history_path = os.path.join(cache_dir, RAW_DATA_FILES['juvenile_history'])
        if os.path.exists(history_path):
            print("   Loading juvenile history...")
            juvenile_history = pd.read_csv(
                filepath_or_buffer=history_path,
                compression="gzip",  # File is compressed
                dtype={
                    "idnJuvenileHistory": "Int64",
                    "idnCase": "Int64",
                    "idnProceeding": "Int64",
                    "idnJuvenile": "category",
                },
                low_memory=False,
            )
            cache.set('juvenile_history', juvenile_history)
            print(f"   ✅ Loaded {len(juvenile_history):,} juvenile history records")
        else:
            print(f"   ⚠️ Optional juvenile history file not found: {history_path}")
            cache.set('juvenile_history', pd.DataFrame())
        
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
        optional_caches = ['juvenile_history', 'lookup_juvenile']
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
        
        # Load optional files if they exist
        for key in optional_caches:
            cache_file_path = os.path.join(cache_dir, CACHE_FILES[key])
            if os.path.exists(cache_file_path):
                with open(cache_file_path, 'rb') as f:
                    cache.set(key, pickle.load(f))
                    print(f"   📁 Loaded {key} from cache")
            else:
                print(f"   ⚠️ Optional {key} cache not found")
                cache.set(key, pd.DataFrame())
        
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
    """Download a file from Google Drive using its file ID with virus scan handling"""
    try:
        print(f"  🌐 Downloading file {file_id}...")
        
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Try multiple URL patterns for Google Drive downloads
        download_urls = [
            # Standard download URL
            f"https://drive.google.com/uc?id={file_id}&export=download",
            # Alternative with confirm parameter
            f"https://drive.google.com/uc?id={file_id}&export=download&confirm=t",
            # Google Drive content URL with authuser
            f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0&confirm=t",
            # Docs URL
            f"https://docs.google.com/uc?export=download&id={file_id}",
        ]
        
        for url_idx, download_url in enumerate(download_urls):
            try:
                print(f"    Trying URL {url_idx + 1}...")
                response = session.get(download_url, stream=True, timeout=120, allow_redirects=True)
                response.raise_for_status()
                
                content_type = response.headers.get('content-type', '').lower()
                content_length = len(response.content) if response.content else 0
                
                print(f"    Response: Content-Type={content_type}, Size={content_length}")
                
                # Check if we got the file directly
                if 'text/html' not in content_type:
                    # Not HTML, likely the file
                    if is_gzipped and response.content.startswith(b'\x1f\x8b'):
                        print(f"  ✅ Downloaded gzipped file successfully")
                        return response.content
                    elif not is_gzipped and content_length > 100:
                        print(f"  ✅ Downloaded file successfully")
                        return response.content
                
                # If we got HTML, check if it's a virus scan confirmation page
                if 'text/html' in content_type and content_length > 500:
                    print(f"    Got HTML response, parsing for download links...")
                    html_content = response.text
                    
                    # Look for the download confirmation link
                    import re
                    
                    # Multiple patterns for Google Drive virus scan bypass
                    patterns = [
                        # Standard patterns
                        r'href="(/uc\?export=download[^"]*)"',
                        r'action="(/uc\?export=download[^"]*)"',
                        # Drive content patterns
                        r'https://drive\.usercontent\.google\.com/download\?id=' + file_id + r'[^"]*',
                        # Confirm token patterns
                        r'confirm=([a-zA-Z0-9\-_]+)',
                        # UUID patterns
                        r'uuid=([a-zA-Z0-9\-]+)',
                        # AT token patterns
                        r'at=([^"&\s]+)'
                    ]
                    
                    # Try to extract and build a proper download URL
                    confirm_match = re.search(r'confirm=([a-zA-Z0-9\-_]+)', html_content)
                    uuid_match = re.search(r'uuid=([a-zA-Z0-9\-]+)', html_content)
                    at_match = re.search(r'at=([^"&\s]+)', html_content)
                    
                    if confirm_match:
                        confirm_token = confirm_match.group(1)
                        print(f"    Found confirm token: {confirm_token[:10]}...")
                        
                        # Build enhanced URL with all parameters
                        enhanced_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&authuser=0&confirm={confirm_token}"
                        
                        if uuid_match:
                            uuid_token = uuid_match.group(1)
                            enhanced_url += f"&uuid={uuid_token}"
                            print(f"    Found UUID: {uuid_token[:10]}...")
                        
                        if at_match:
                            at_token = at_match.group(1)
                            enhanced_url += f"&at={at_token}"
                            print(f"    Found AT token: {at_token[:20]}...")
                        
                        print(f"    Trying enhanced URL...")
                        
                        # Try the enhanced URL
                        response2 = session.get(enhanced_url, stream=True, timeout=120, allow_redirects=True)
                        response2.raise_for_status()
                        
                        if response2.content and len(response2.content) > 1000:
                            content_type2 = response2.headers.get('content-type', '').lower()
                            if 'text/html' not in content_type2:
                                print(f"  ✅ Enhanced URL download successful")
                                return response2.content
                    
                    # Look for direct download links in HTML
                    download_link_patterns = [
                        r'href="(https://drive\.usercontent\.google\.com/download[^"]*)"',
                        r'"downloadUrl":"([^"]*)"',
                        r'action="([^"]*uc\?export=download[^"]*)"'
                    ]
                    
                    for pattern in download_link_patterns:
                        match = re.search(pattern, html_content)
                        if match:
                            found_url = match.group(1)
                            if found_url.startswith('/'):
                                found_url = 'https://drive.google.com' + found_url
                            found_url = found_url.replace('\\u0026', '&').replace('&amp;', '&')
                            
                            print(f"    Found direct link: {found_url[:100]}...")
                            
                            try:
                                response3 = session.get(found_url, stream=True, timeout=120, allow_redirects=True)
                                response3.raise_for_status()
                                
                                if response3.content and len(response3.content) > 1000:
                                    content_type3 = response3.headers.get('content-type', '').lower()
                                    if 'text/html' not in content_type3:
                                        print(f"  ✅ Direct link download successful")
                                        return response3.content
                            except:
                                continue
                
                print(f"    URL {url_idx + 1} didn't provide valid file")
                
            except Exception as e:
                print(f"    URL {url_idx + 1} failed: {e}")
                continue
        
        print(f"  ❌ All download attempts failed for {file_id}")
        return None
            
    except Exception as e:
        print(f"  ❌ Error downloading file {file_id}: {e}")
        return None

def download_raw_files_from_google_drive():
    """Download raw data files from Google Drive and save to cache directory (skip existing files)"""
    try:
        cache_dir = get_cache_dir()
        print("🌐 Checking and downloading missing raw data files from Google Drive...")
        
        downloaded_count = 0
        skipped_count = 0
        
        # Download each file and save to cache (only if not already exists)
        for file_key, filename in RAW_DATA_FILES.items():
            file_path = os.path.join(cache_dir, filename)
            
            # Skip if file already exists
            if os.path.exists(file_path):
                print(f"📁 {filename} already exists in cache, skipping...")
                skipped_count += 1
                continue
                
            if file_key in GOOGLE_DRIVE_FILES:
                file_id = GOOGLE_DRIVE_FILES[file_key]
                print(f"📊 Downloading {filename}...")
                
                # Determine if file is gzipped based on extension
                is_gzipped = filename.endswith('.gz')
                content = download_from_google_drive(file_id, is_gzipped)
                
                if content is not None:
                    # Save raw file to cache directory
                    with open(file_path, 'wb') as f:
                        f.write(content)
                    print(f"  ✅ Saved {filename} to cache ({len(content)} bytes)")
                    downloaded_count += 1
                else:
                    print(f"  ❌ Failed to download {filename}")
            else:
                print(f"  ⚠️ No Google Drive ID found for {filename}")
        
        print(f"📥 Summary: {downloaded_count} downloaded, {skipped_count} skipped (already in cache)")
        return (downloaded_count + skipped_count) > 0
        
    except Exception as e:
        print(f"❌ Error downloading files from Google Drive: {e}")
        return False

def load_data():
    """Load and process datasets - only real data, no mock data"""
    # Check if data is already loaded and processed
    if cache.is_loaded():
        # Verify that analysis_filtered exists, if not process it
        analysis_filtered = cache.get('analysis_filtered')
        if analysis_filtered is not None and not analysis_filtered.empty:
            print("✅ Data already loaded and processed in cache - skipping reload")
            return True
        else:
            print("📊 Raw data loaded but analysis missing, processing...")
            try:
                from .data_processor import process_analysis_data
            except ImportError:
                from data_processor import process_analysis_data
            process_analysis_data()
            save_to_cache()  # Update cache with analysis
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
