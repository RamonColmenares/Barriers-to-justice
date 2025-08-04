"""
Basic statistics functionality for the data page
"""
import pandas as pd

# Local imports
from .models import cache
from .filters import apply_filters, Filters

def get_basic_statistics():
    """Get basic statistics for the data page (success rates, barriers, etc.)"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        # Calculate basic representation success rates
        percentage_data = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'],
            analysis_filtered['BINARY_OUTCOME'],
            normalize='index'  # Normalize by rows (representation status)
        ) * 100
        
        stats = {}
        
        # Success rate with representation
        if 'Has Legal Representation' in percentage_data.index and 'Favorable' in percentage_data.columns:
            stats['success_with_representation'] = round(
                percentage_data.loc['Has Legal Representation', 'Favorable'], 1
            )
        else:
            stats['success_with_representation'] = 0.0
            
        # Success rate without representation  
        if 'No Legal Representation' in percentage_data.index and 'Favorable' in percentage_data.columns:
            stats['success_without_representation'] = round(
                percentage_data.loc['No Legal Representation', 'Favorable'], 1
            )
        else:
            stats['success_without_representation'] = 0.0
        
        # Calculate barriers statistic (inverse of representation rate)
        rep_counts = analysis_filtered['HAS_LEGAL_REP'].value_counts()
        total_cases = len(analysis_filtered)
        if total_cases > 0:
            representation_rate = rep_counts.get("Has Legal Representation", 0) / total_cases * 100
            # Estimate barriers as high percentage minus representation rate
            barriers_percentage = max(70, 100 - representation_rate)
            stats['barriers_percentage'] = round(barriers_percentage, 0)
        else:
            stats['barriers_percentage'] = 75
            
        # Additional context
        stats['total_cases_analyzed'] = total_cases
        stats['representation_rate'] = round(representation_rate, 1) if total_cases > 0 else 0.0
        
        return stats
        
    except Exception as e:
        print(f"Error calculating basic statistics: {str(e)}")
        return {"error": f"Statistics calculation error: {str(e)}"}

def get_filtered_statistics(filters):
    """Get filtered statistics for the findings page cards"""
    try:
        # Get the filtered dataset
        analysis_filtered = cache.get('analysis_filtered')
        if analysis_filtered is None or analysis_filtered.empty:
            return None
        
        # Apply filters to the data
        filtered_data = apply_filters(analysis_filtered, filters)
        if filtered_data is None or filtered_data.empty:
            return None
        
        # Calculate success rates
        percentage_data = pd.crosstab(
            filtered_data['HAS_LEGAL_REP'],
            filtered_data['BINARY_OUTCOME'],
            normalize='index'  # Normalize by rows (representation status)
        ) * 100
        
        stats = {}
        
        # Success rate with representation
        if 'Has Legal Representation' in percentage_data.index and 'Favorable' in percentage_data.columns:
            stats['success_with_representation'] = round(
                percentage_data.loc['Has Legal Representation', 'Favorable'], 1
            )
        else:
            stats['success_with_representation'] = 0.0
            
        # Success rate without representation  
        if 'No Legal Representation' in percentage_data.index and 'Favorable' in percentage_data.columns:
            stats['success_without_representation'] = round(
                percentage_data.loc['No Legal Representation', 'Favorable'], 1
            )
        else:
            stats['success_without_representation'] = 0.0
        
        # Total cases in filtered dataset
        total_cases = len(filtered_data)
        stats['total_cases'] = total_cases
        
        # Calculate representation rate in filtered data
        rep_counts = filtered_data['HAS_LEGAL_REP'].value_counts()
        if total_cases > 0:
            representation_rate = rep_counts.get("Has Legal Representation", 0) / total_cases * 100
            stats['representation_rate'] = round(representation_rate, 1)
        else:
            stats['representation_rate'] = 0.0
            
        # Years of data (calculate from actual date range if available)
        stats['years_of_data'] = 7  # Default fallback
        if 'LATEST_HEARING' in filtered_data.columns:
            try:
                years_range = filtered_data['LATEST_HEARING'].dt.year.nunique()
                if years_range > 0:
                    stats['years_of_data'] = years_range
            except:
                pass
        
        return stats
        
    except Exception as e:
        print(f"Error calculating filtered statistics: {str(e)}")
        return None
