"""
Data processing and analysis functionality for the juvenile immigration API
"""
import pandas as pd
import numpy as np
import traceback
from datetime import datetime

try:
    from .config import FAVORABLE_DECISIONS, UNFAVORABLE_DECISIONS, OTHER_DECISIONS
    from .models import cache
except ImportError:
    from config import FAVORABLE_DECISIONS, UNFAVORABLE_DECISIONS, OTHER_DECISIONS
    from models import cache

def determine_policy_era(date):
    """Determine policy era based on date"""
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

def categorize_outcome(dec_code):
    """Categorize outcome based on decision code"""
    if pd.isna(dec_code):
        return "Unknown"
    elif dec_code in FAVORABLE_DECISIONS:
        return "Favorable" 
    elif dec_code in UNFAVORABLE_DECISIONS:
        return "Unfavorable"
    else:
        return "Other"

def process_analysis_data():
    """Process data for analysis exactly like in the notebook - handle empty data gracefully"""
    try:
        juvenile_cases = cache.get('juvenile_cases')
        proceedings = cache.get('proceedings')
        reps_assigned = cache.get('reps_assigned')
        lookup_decisions = cache.get('lookup_decisions')
        
        if (juvenile_cases is None or 
            proceedings is None or 
            reps_assigned is None or
            lookup_decisions is None):
            print("❌ Cannot process analysis data - missing datasets")
            return False
        
        # Check if we have empty DataFrames
        if (juvenile_cases.empty or 
            proceedings.empty or 
            lookup_decisions.empty):
            print("⚠️ Processing empty datasets - creating minimal analysis structure")
            
            # Create minimal empty analysis_filtered
            analysis_filtered = pd.DataFrame(columns=[
                'IDNCASE', 'HAS_LEGAL_REP', 'BINARY_OUTCOME', 'POLICY_ERA', 
                'REPRESENTATION_LEVEL', 'DEC_CODE', 'decision_description',
                'COMP_DATE', 'LATEST_HEARING', 'hearing_date_combined'
            ])
            cache.set('analysis_filtered', analysis_filtered)
            
            print("✅ Empty analysis data structure created")
            return True
            
        print("Processing analysis data exactly like notebook...")
        
        # Step 1: Merge proceedings with decision descriptions (EXACTLY like notebook)
        proceedings_with_decisions = proceedings[
            ['IDNCASE', 'COMP_DATE', 'NAT', 'LANG', 'CASE_TYPE', 'DEC_CODE']
        ].merge(
            lookup_decisions[['strCode', 'strDescription']],  # Use strCode from lookup table
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
        merged_data = juvenile_cases[
            ['IDNCASE', 'NAT', 'LANG', 'CASE_TYPE', 'Sex', 'C_BIRTHDATE', 'LATEST_HEARING']
        ].merge(
            proceedings_with_decisions[['IDNCASE', 'COMP_DATE', 'DEC_CODE', 'decision_description']],
            left_on='IDNCASE',
            right_on='IDNCASE',
            how='left'
        )
        
        # Step 3: Merge with reps_assigned (EXACTLY like notebook)
        if not reps_assigned.empty:
            merged_data = merged_data.merge(
                reps_assigned[['IDNCASE', 'STRATTYLEVEL']], 
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
        merged_data['POLICY_ERA'] = merged_data['hearing_date_combined'].apply(determine_policy_era)
        
        # Step 7: Create legal representation indicator EXACTLY like notebook
        merged_data['HAS_LEGAL_REP'] = merged_data['REPRESENTATION_LEVEL'].apply(
            lambda x: "No Legal Representation"
            if x == "no_representation"
            else ("Has Legal Representation" if x == "COURT" or x == "BOARD" else "Unknown")
        )
        
        # Step 8: Create binary outcome classification EXACTLY like notebook
        merged_data['BINARY_OUTCOME'] = merged_data['DEC_CODE'].apply(categorize_outcome)
        merged_data['CASE_OUTCOME'] = merged_data.get('decision_description', '')
        
        # Step 9: Create analysis_filtered EXACTLY like notebook
        analysis_filtered = merged_data[
            (merged_data['HAS_LEGAL_REP'] != "Unknown") &
            (merged_data['BINARY_OUTCOME'] != "Unknown") &
            (merged_data['BINARY_OUTCOME'] != "Other")
        ].copy()
        
        # Store processed data
        cache.set('merged_data', merged_data)
        cache.set('analysis_filtered', analysis_filtered)
        
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
        traceback.print_exc()
        
        # Create minimal empty analysis_filtered to prevent explosions
        analysis_filtered = pd.DataFrame(columns=[
            'IDNCASE', 'HAS_LEGAL_REP', 'BINARY_OUTCOME', 'POLICY_ERA', 
            'REPRESENTATION_LEVEL', 'DEC_CODE', 'decision_description',
            'COMP_DATE', 'LATEST_HEARING', 'hearing_date_combined'
        ])
        cache.set('analysis_filtered', analysis_filtered)
        
        return True  # Return True to prevent further explosions

def get_data_statistics():
    """Calculate real statistics from the loaded data"""
    if not cache.is_loaded() or cache.get('juvenile_cases') is None:
        return None
    
    try:
        juvenile_cases = cache.get('juvenile_cases')
        reps_assigned = cache.get('reps_assigned')
        
        # Calculate basic statistics
        total_cases = len(juvenile_cases)
        
        # Nationality distribution
        nat_counts = juvenile_cases['NAT'].value_counts().head(10).to_dict()
        
        # Language distribution  
        lang_counts = juvenile_cases['LANG'].value_counts().to_dict()
        
        # Custody distribution
        custody_counts = juvenile_cases['CUSTODY'].value_counts().to_dict()
        
        # Case type distribution
        case_type_counts = juvenile_cases['CASE_TYPE'].value_counts().to_dict()
        
        # Gender distribution
        gender_counts = juvenile_cases['Sex'].value_counts().to_dict()
        
        # Calculate representation statistics
        rep_stats = {}
        if reps_assigned is not None:
            # Merge with reps data to get representation info
            cases_with_rep = juvenile_cases.merge(reps_assigned, on='IDNCASE', how='left')
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
        if 'C_BIRTHDATE' in juvenile_cases.columns:
            current_date = pd.Timestamp.now()
            ages = (current_date - juvenile_cases['C_BIRTHDATE']).dt.days / 365.25
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
