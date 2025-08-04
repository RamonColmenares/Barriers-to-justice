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

def calculate_age(birthdate, hearing_date):
    """Calculate age at filing EXACTLY like notebook"""
    if pd.isna(birthdate) or pd.isna(hearing_date):
        return None

    # Convert string dates to datetime if needed
    if isinstance(birthdate, str):
        try:
            birthdate = pd.to_datetime(birthdate)
        except Exception:
            return None

    if isinstance(hearing_date, str):
        try:
            hearing_date = pd.to_datetime(hearing_date)
        except Exception:
            return None

    # Now both should be datetime objects for subtraction
    age = (hearing_date - birthdate).days / 365.25
    return age

def process_analysis_data():
    """Process data for analysis exactly like in the notebook - load data with correct dtypes"""
    try:
        print("Loading data with proper dtypes EXACTLY like notebook...")
        
        # Load juvenile history data EXACTLY like notebook
        juvenile_history = cache.get('juvenile_history')
        if juvenile_history is None:
            print("⚠️ Juvenile history data not available, skipping")
            juvenile_history = pd.DataFrame()
        
        # Load juvenile cases with EXACT dtype specification from notebook
        juvenile_cases = cache.get('juvenile_cases')
        proceedings = cache.get('proceedings') 
        reps_assigned = cache.get('reps_assigned')
        lookup_decisions = cache.get('lookup_decisions')
        lookup_juvenile = cache.get('lookup_juvenile')
        
        if (juvenile_cases is None or 
            proceedings is None or 
            lookup_decisions is None):
            print("❌ Cannot process analysis data - missing core datasets")
            return False
        
        # Print data types for all tables EXACTLY like notebook
        print("### Data Types for All Tables")
        if not juvenile_history.empty:
            print("**Juvenile History Data Types:**")
            print(juvenile_history.dtypes.to_frame("dtype"))
        
        print("**Cases Data Types:**")
        print(juvenile_cases.dtypes.to_frame("dtype"))
        
        if reps_assigned is not None and not reps_assigned.empty:
            print("**Reps Assigned Data Types:**")
            print(reps_assigned.dtypes.to_frame("dtype"))
        
        print("**Proceedings Data Types:**")
        print(proceedings.dtypes.to_frame("dtype"))
        
        print("\nStarting clean process EXACTLY like notebook...")
        
        # Step 1: Merge proceedings data with decision description column from lookup_decisions
        # Keep only relevant columns from proceedings that will be used in the analysis
        proceedings_with_decisions = proceedings[
            [
                "IDNCASE",
                "COMP_DATE", 
                "NAT",
                "LANG",
                "CASE_TYPE",
                "DEC_CODE",
            ]
        ].merge(
            lookup_decisions[["strCode", "strDescription"]],  # Use strCode from lookup table
            how="left",
            left_on="DEC_CODE",  # Column in proceedings table
            right_on="strCode",  # Column in lookup table
        )

        # Drop the strCode column after merging because it contains same information as DEC_CODE
        proceedings_with_decisions = proceedings_with_decisions.drop(columns=["strCode"])

        # Rename the strDescription column to avoid conflict in later merges
        proceedings_with_decisions = proceedings_with_decisions.rename(
            columns={"strDescription": "decision_description"}
        )

        # Create a merged dataset: juvenile_cases + proceedings_with_decisions + reps_assigned
        # Keep only relevant columns from each dataset

        # First merge juvenile_cases with proceedings_with_decisions keep only relevant columns
        merged_data = juvenile_cases[
            [
                "IDNCASE",
                "NAT", 
                "LANG",
                "CASE_TYPE",
                "Sex",
                "C_BIRTHDATE",
                "LATEST_HEARING",
            ]
        ].merge(
            proceedings_with_decisions[
                ["IDNCASE", "COMP_DATE", "DEC_CODE", "decision_description"]
            ],
            left_on="IDNCASE",
            right_on="IDNCASE",
            how="left",
        )

        # Second: Merge with reps_assigned, keeping all rows from merged_data
        if reps_assigned is not None and not reps_assigned.empty:
            merged_data = merged_data.merge(
                reps_assigned[["IDNCASE", "STRATTYLEVEL"]], on="IDNCASE", how="left"
            )
        else:
            # Add empty STRATTYLEVEL column if reps_assigned is empty
            merged_data['STRATTYLEVEL'] = pd.Categorical([])

        # Fill missing STRATTYLEVEL values with "no_representation"
        # Add "no representation" as a valid category
        if 'STRATTYLEVEL' in merged_data.columns:
            # Convert to categorical if not already
            if not pd.api.types.is_categorical_dtype(merged_data['STRATTYLEVEL']):
                merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].astype('category')
            
            merged_data["STRATTYLEVEL"] = merged_data["STRATTYLEVEL"].cat.add_categories(
                ["no_representation"]
            )
            # Fill missing values in STRATTYLEVEL with "no_representation"
            merged_data["STRATTYLEVEL"] = merged_data["STRATTYLEVEL"].fillna("no_representation")
        else:
            merged_data['STRATTYLEVEL'] = pd.Categorical(['no_representation'] * len(merged_data))

        # Changing STRATTYLEVEL name to "REPRESENTATION_LEVEL"
        merged_data = merged_data.rename(columns={"STRATTYLEVEL": "REPRESENTATION_LEVEL"})

        print("Sample row from merged dataset:")
        print(merged_data.head(5))

        # Before creating hearing_date_combined, ensure both columns are datetime
        # Check if COMP_DATE needs conversion
        if merged_data["COMP_DATE"].dtype == "object":
            merged_data["COMP_DATE"] = pd.to_datetime(merged_data["COMP_DATE"], errors="coerce")

        # Check if LATEST_HEARING needs conversion  
        if merged_data["LATEST_HEARING"].dtype == "object":
            merged_data["LATEST_HEARING"] = pd.to_datetime(
                merged_data["LATEST_HEARING"], errors="coerce"
            )
        
        # Now create the combined date field
        merged_data["hearing_date_combined"] = merged_data["COMP_DATE"].fillna(
            merged_data["LATEST_HEARING"]
        )

        # Calculate age using the enhanced function
        merged_data["AGE_AT_FILING"] = merged_data.apply(
            lambda row: calculate_age(row["C_BIRTHDATE"], row["hearing_date_combined"]), axis=1
        )

        # Determine policy era
        merged_data["POLICY_ERA"] = merged_data["hearing_date_combined"].apply(
            determine_policy_era
        )

        # NOTE: Detention duration calculation is skipped because the DATE_RELEASED column
        # is empty or doesn't exist in the dataset
        print(
            "NOTE: Detention duration analysis skipped due to missing or empty DATE_RELEASED data"
        )
        
        # Create HAS_LEGAL_REP indicator EXACTLY like notebook
        merged_data["HAS_LEGAL_REP"] = merged_data["REPRESENTATION_LEVEL"].apply(
            lambda x: "No Legal Representation"
            if x == "no_representation"
            else ("Has Legal Representation" if x == "COURT" or x == "BOARD" else "Unknown")
        )

        # Display summary of the data we were able to analyze
        print("\nSummary of available data:")
        print(f"Total records: {len(merged_data):,}")
        print(f"Records with age calculation: {merged_data['AGE_AT_FILING'].notna().sum():,}")
        print(f"Policy era distribution:\n{merged_data['POLICY_ERA'].value_counts()}")
        print(
            f"Legal representation distribution:\n{merged_data['HAS_LEGAL_REP'].value_counts()}"
        )

        # Create binary outcome categories based on actual decision codes
        merged_data["BINARY_OUTCOME"] = merged_data["DEC_CODE"].apply(categorize_outcome)

        # Using decision_description instead of DECISION_DESCRIPTION  
        merged_data["CASE_OUTCOME"] = merged_data["decision_description"]

        # Create an analysis dataset with key columns that exist
        # Core analysis columns we want if they exist
        available_columns = []
        possible_columns = [
            "IDNCASE",
            "hearing_date_combined",
            "C_BIRTHDATE", 
            "Sex",
            "AGE_AT_FILING",
            "POLICY_ERA",
            "HAS_LEGAL_REP", 
            "DEC_CODE",
            "CASE_OUTCOME",
            "BINARY_OUTCOME",
            "REPRESENTATION_LEVEL"
        ]

        # Add columns that exist to our selection list
        for column in possible_columns:
            if column in merged_data.columns:
                available_columns.append(column)

        # Create the analysis dataframe with only available columns
        analysis_df = merged_data[available_columns]

        # Examine the analysis dataset
        print("First 5 rows of the analysis dataset:")
        print(analysis_df.head(5))

        # Filter to cases with known representation status and outcomes for analysis
        analysis_filtered = analysis_df[
            (analysis_df["HAS_LEGAL_REP"] != "Unknown")
            & (analysis_df["BINARY_OUTCOME"] != "Unknown")
            & (analysis_df["BINARY_OUTCOME"] != "Other")
        ].copy()

        # Check the distribution of representation after filtering
        print("Legal representation distribution (filtered dataset):")
        rep_counts = analysis_filtered["HAS_LEGAL_REP"].value_counts()
        print(rep_counts)

        # Calculate overall representation rate
        if len(analysis_filtered) > 0:
            rep_rate = rep_counts.get("Has Legal Representation", 0) / len(analysis_filtered) * 100
            print(f"\nLegal Representation Rate: {rep_rate:.2f}%")
        else:
            print("\nNo filtered data available for representation rate calculation")

        # Examine the relationship between legal representation and case outcomes
        print("\nOutcome Distribution by Legal Representation:")
        if len(analysis_filtered) > 0:
            outcome_by_rep = pd.crosstab(
                analysis_filtered["BINARY_OUTCOME"], analysis_filtered["HAS_LEGAL_REP"]
            )
            print(outcome_by_rep)

            # Calculate percentages
            outcome_by_rep_pct = (
                pd.crosstab(
                    analysis_filtered["BINARY_OUTCOME"],
                    analysis_filtered["HAS_LEGAL_REP"],
                    normalize="columns",  # Normalize by columns to get percentages within each representation category
                )
                * 100
            )

            print("\nOutcome Percentages by Legal Representation:")
            print(outcome_by_rep_pct)

        # Store processed data
        cache.set('merged_data', merged_data)
        cache.set('analysis_filtered', analysis_filtered)
        
        print(f"Analysis data processed successfully!")
        print(f"Total merged records: {len(merged_data):,}")
        print(f"Filtered analysis records: {len(analysis_filtered):,}")
        
        return True
        
    except Exception as e:
        print(f"Error processing analysis data: {str(e)}")
        traceback.print_exc()
        
        # Create minimal empty analysis_filtered to prevent explosions
        analysis_filtered = pd.DataFrame(columns=[
            'IDNCASE', 'HAS_LEGAL_REP', 'BINARY_OUTCOME', 'POLICY_ERA', 
            'REPRESENTATION_LEVEL', 'DEC_CODE', 'decision_description',
            'COMP_DATE', 'LATEST_HEARING', 'hearing_date_combined', 'AGE_AT_FILING'
        ])
        cache.set('analysis_filtered', analysis_filtered)
        
        return True  # Return True to prevent further explosions

def get_data_statistics(juvenile_cases_data=None):
    """Calculate real statistics from the loaded data or provided data"""
    if juvenile_cases_data is None:
        if not cache.is_loaded() or cache.get('juvenile_cases') is None:
            return None
        juvenile_cases = cache.get('juvenile_cases')
        reps_assigned = cache.get('reps_assigned')
    else:
        juvenile_cases = juvenile_cases_data
        reps_assigned = cache.get('reps_assigned')  # Use cached reps data
    
    try:
        
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
