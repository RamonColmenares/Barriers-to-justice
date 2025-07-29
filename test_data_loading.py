#!/usr/bin/env python3
"""
Test script to verify data loading functionality
"""
import sys
import os

# Add the api directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'api'))

from data_loader import load_data, check_raw_files_in_cache, download_raw_files_from_google_drive
from models import cache

def test_data_loading():
    """Test the data loading functionality"""
    print("🔍 Testing data loading functionality...")
    
    print("\n1. Checking for raw files in cache...")
    has_raw_files = check_raw_files_in_cache()
    
    if not has_raw_files:
        print("\n2. No raw files found, attempting to download from Google Drive...")
        download_success = download_raw_files_from_google_drive()
        if not download_success:
            print("❌ Failed to download files from Google Drive")
            return False
    
    print("\n3. Attempting to load data...")
    load_success = load_data()
    
    if load_success:
        print("✅ Data loaded successfully!")
        
        # Print summary
        stats = cache.get_stats()
        print(f"\n📊 Data Summary:")
        print(f"   Cases: {stats.get('juvenile_cases', 0):,}")
        print(f"   Proceedings: {stats.get('proceedings', 0):,}")
        print(f"   Representations: {stats.get('reps_assigned', 0):,}")
        print(f"   Decision codes: {stats.get('lookup_decisions', 0)}")
        print(f"   Analysis data: {stats.get('analysis_filtered', 0):,}")
        
        return True
    else:
        print("❌ Failed to load data")
        return False

if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1)
