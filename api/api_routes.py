"""
API route handlers for the juvenile immigration API
"""
from flask import jsonify, request
from datetime import datetime

# Local imports
from .data_loader import load_data, download_raw_files_from_google_drive, save_to_cache
from .data_processor import get_data_statistics, process_analysis_data
from .chart_generator import (
    generate_representation_outcomes_chart,
    generate_time_series_chart,
    generate_chi_square_analysis,
    generate_outcome_percentages_chart,
    generate_countries_chart
)
from .basic_stats import get_basic_statistics, get_filtered_statistics
from .models import cache
from .filters import Filters, filter_options

def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "juvenile-immigration-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


def meta_options():
    """Return available filter options derived from the data"""
    try:
        if not load_data():
            return jsonify({"error": "No data loaded"}), 500
        analysis_filtered = cache.get('analysis_filtered')
        from .filters import filter_options
        opts = filter_options(analysis_filtered if analysis_filtered is not None else cache.get('merged_data'))
        return jsonify({"options": opts})
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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
        juvenile_cases = cache.get('juvenile_cases')
        if juvenile_cases is not None and 'LATEST_HEARING' in juvenile_cases.columns:
            try:
                # Filter only historical data (not future scheduled hearings)
                import pandas as pd
                current_date = pd.Timestamp.now()
                
                # Group by month for trends - only historical data
                historical_data = juvenile_cases[
                    (juvenile_cases['LATEST_HEARING'].notna()) & 
                    (juvenile_cases['LATEST_HEARING'] <= current_date)
                ].copy()
                
                if len(historical_data) > 0:
                    historical_data['month'] = historical_data['LATEST_HEARING'].dt.to_period('M')
                    monthly_counts = historical_data.groupby('month').size()
                    
                    # Convert to dictionary for JSON serialization - last 12 months
                    trends = {
                        "monthly_cases": {
                            str(month): count for month, count in monthly_counts.tail(12).items()
                        }
                    }
                else:
                    trends = {"monthly_cases": {}}
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

def load_data_endpoint():
    """Endpoint to trigger data loading"""
    try:
        success = load_data()
        if success:
            stats = cache.get_stats()
            return jsonify({
                "status": "success",
                "message": "Data loaded successfully",
                "cases_count": stats.get('juvenile_cases', 0),
                "proceedings_count": stats.get('proceedings', 0),
                "reps_count": stats.get('reps_assigned', 0),
                "data_source": "Real Data"
            })
        else:
            return jsonify({"error": "Failed to load data"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def force_reload_data():
    """Force reload data from Google Drive (clear cache first)"""
    try:
        # Clear cache
        cache.clear()
        
        # Force download from Google Drive
        success = download_raw_files_from_google_drive()
        if success:
            # Load the downloaded files
            success = load_data()
            if success:
                stats = cache.get_stats()
                return jsonify({
                    "status": "success",
                    "message": "Data force-reloaded from Google Drive",
                    "cases_count": stats.get('juvenile_cases', 0),
                    "proceedings_count": stats.get('proceedings', 0),
                    "reps_count": stats.get('reps_assigned', 0),
                    "analysis_count": stats.get('analysis_filtered', 0)
                })
        
        return jsonify({"error": "Failed to reload data from Google Drive"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def data_status():
    """Check if data is loaded and get basic info"""
    try:
        stats = cache.get_stats()
        return jsonify({
            "data_loaded": cache.is_loaded(),
            "cases_loaded": cache.get('juvenile_cases') is not None,
            "proceedings_loaded": cache.get('proceedings') is not None,
            "reps_loaded": cache.get('reps_assigned') is not None,
            "lookup_loaded": cache.get('lookup_decisions') is not None,
            "lookup_juvenile_loaded": cache.get('lookup_juvenile') is not None,
            "cases_count": stats.get('juvenile_cases', 0),
            "proceedings_count": stats.get('proceedings', 0),
            "reps_count": stats.get('reps_assigned', 0)
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def representation_outcomes():
    """Generate Plotly chart data for representation vs outcomes chart (EXACTLY like notebook)"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        chart_data = generate_representation_outcomes_chart(filters.to_dict())
        if "error" in chart_data:
            return jsonify(chart_data), 500
        
        return chart_data
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def time_series_analysis():
    """Generate Plotly time series chart exactly like notebook"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        chart_data = generate_time_series_chart(filters.to_dict())
        if "error" in chart_data:
            return jsonify(chart_data), 500
        
        return chart_data
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def chi_square_analysis():
    """Generate chi-square analysis results (like notebook) - handle empty data gracefully"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        results = generate_chi_square_analysis(filters.to_dict())
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def outcome_percentages():
    """Generate the percentage breakdown chart EXACTLY like notebook"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        chart_data = generate_outcome_percentages_chart(filters.to_dict())
        if "error" in chart_data:
            return jsonify(chart_data), 500
        
        return chart_data
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def countries_chart():
    """Generate the countries by case volume chart with enhanced hover tooltips"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        chart_data = generate_countries_chart(filters.to_dict())
        if "error" in chart_data:
            return jsonify(chart_data), 500
        
        return chart_data
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def basic_statistics():
    """Get basic statistics for the data page"""
    try:
        # Load data if needed
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        stats = get_basic_statistics()
        if "error" in stats:
            return jsonify(stats), 500
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def get_filtered_overview():
    """Get overview statistics with filters applied"""
    try:
        # Load data if not already loaded
        if not load_data():
            return jsonify({"error": "Failed to load data"}), 500
        
        # Get filter parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        # Get filtered statistics
        filtered_stats = get_filtered_statistics(filters)
        if filtered_stats is None:
            return jsonify({"error": "Failed to calculate filtered statistics"}), 500
        
        return jsonify(filtered_stats)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def get_all_findings_data():
    """Get all findings chart data in a single request to reduce API calls"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from .filters import Filters
        filters = Filters.from_query(request.args)
        
        results = {}
        errors = []
        
        # Try to generate each chart, handling errors individually
        try:
            results['representationOutcomes'] = generate_representation_outcomes_chart(filters)
        except Exception as e:
            results['representationOutcomes'] = {"error": f"Representation chart error: {str(e)}"}
            errors.append(f"Representation outcomes: {str(e)}")
        
        try:
            results['timeSeriesAnalysis'] = generate_time_series_chart(filters)
        except Exception as e:
            results['timeSeriesAnalysis'] = {"error": f"Time series chart error: {str(e)}"}
            errors.append(f"Time series analysis: {str(e)}")
        
        try:
            results['chiSquareAnalysis'] = generate_chi_square_analysis(filters)
        except Exception as e:
            results['chiSquareAnalysis'] = {"error": f"Chi-square analysis error: {str(e)}"}
            errors.append(f"Chi-square analysis: {str(e)}")
        
        try:
            results['outcomePercentages'] = generate_outcome_percentages_chart(filters)
        except Exception as e:
            results['outcomePercentages'] = {"error": f"Outcome percentages error: {str(e)}"}
            errors.append(f"Outcome percentages: {str(e)}")
        
        try:
            results['countriesChart'] = generate_countries_chart(filters)
        except Exception as e:
            results['countriesChart'] = {"error": f"Countries chart error: {str(e)}"}
            errors.append(f"Countries chart: {str(e)}")
        
        # Include error summary if any occurred
        if errors:
            results['errors'] = errors
            results['partial_success'] = True
        else:
            results['success'] = True
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
