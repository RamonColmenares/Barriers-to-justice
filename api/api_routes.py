"""
API route handlers for the juvenile immigration API
"""
from flask import jsonify
from datetime import datetime

try:
    from .data_loader import load_data, download_raw_files_from_google_drive, save_to_cache
    from .data_processor import get_data_statistics, process_analysis_data
    from .chart_generator import (
        generate_representation_outcomes_chart,
        generate_time_series_chart,
        generate_chi_square_analysis,
        generate_outcome_percentages_chart,
        generate_countries_chart
    )
    from .basic_stats import get_basic_statistics
    from .models import cache
except ImportError:
    from data_loader import load_data, download_raw_files_from_google_drive, save_to_cache
    from data_processor import get_data_statistics, process_analysis_data
    from chart_generator import (
        generate_representation_outcomes_chart,
        generate_time_series_chart,
        generate_chi_square_analysis,
        generate_outcome_percentages_chart,
        generate_countries_chart
    )
    from basic_stats import get_basic_statistics
    from models import cache

def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "juvenile-immigration-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })

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
                # Group by month for trends
                monthly_data = juvenile_cases.copy()
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
        from flask import request
        filters = {
            'time_period': request.args.get('time_period', 'all'),
            'representation': request.args.get('representation', 'all'),
            'case_type': request.args.get('case_type', 'all')
        }
        
        chart_data = generate_representation_outcomes_chart(filters)
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
        from flask import request
        filters = {
            'time_period': request.args.get('time_period', 'all'),
            'representation': request.args.get('representation', 'all'),
            'case_type': request.args.get('case_type', 'all')
        }
        
        chart_data = generate_time_series_chart(filters)
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
        from flask import request
        filters = {
            'time_period': request.args.get('time_period', 'all'),
            'representation': request.args.get('representation', 'all'),
            'case_type': request.args.get('case_type', 'all')
        }
        
        results = generate_chi_square_analysis(filters)
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

def outcome_percentages():
    """Generate the percentage breakdown chart EXACTLY like notebook"""
    try:
        if not load_data():
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Get filters from request parameters
        from flask import request
        filters = {
            'time_period': request.args.get('time_period', 'all'),
            'representation': request.args.get('representation', 'all'),
            'case_type': request.args.get('case_type', 'all')
        }
        
        chart_data = generate_outcome_percentages_chart(filters)
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
        from flask import request
        filters = {
            'time_period': request.args.get('time_period', 'all'),
            'representation': request.args.get('representation', 'all'),
            'case_type': request.args.get('case_type', 'all')
        }
        
        chart_data = generate_countries_chart(filters)
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
