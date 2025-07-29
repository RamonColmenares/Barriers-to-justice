"""
Basic statistics functionality for the data page
"""
import pandas as pd

try:
    from .models import cache
except ImportError:
    from models import cache

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
