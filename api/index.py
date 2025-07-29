from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import plotly.express as px
import plotly.graph_objects as go
from plotly.utils import PlotlyJSONEncoder

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['DEBUG'] = False

# Sample data generator for demonstration
def load_real_data():
    """Load real immigration data from the analysis datasets"""
    try:
        print("🔄 Loading real juvenile immigration datasets...")
        
        # Vercel doesn't support file mounting, so we'll use sample data
        # In production, you'd use a database or external storage
        print("⚠️  Using sample data - connect to database for production")
        return generate_sample_data()
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return generate_sample_data()

def generate_sample_data():
    """Generate sample data for demonstration"""
    np.random.seed(42)
    
    # Sample juvenile cases
    n_cases = 1000
    juvenile_cases = pd.DataFrame({
        'IDNCASE': range(1, n_cases + 1),
        'NAT': np.random.choice(['Mexico', 'Guatemala', 'El Salvador', 'Honduras', 'Other'], n_cases),
        'LANG': np.random.choice(['Spanish', 'English', 'Other'], n_cases, p=[0.7, 0.2, 0.1]),
        'CUSTODY': np.random.choice(['Released', 'Detained'], n_cases, p=[0.6, 0.4]),
        'CASE_TYPE': np.random.choice(['Removal', 'Asylum', 'Other'], n_cases, p=[0.5, 0.3, 0.2]),
        'Sex': np.random.choice(['M', 'F'], n_cases),
        'AGE_AT_ENTRY': np.random.randint(5, 18, n_cases),
        'LATEST_HEARING': pd.date_range('2020-01-01', '2024-12-31', periods=n_cases),
        'DATE_OF_ENTRY': pd.date_range('2018-01-01', '2024-01-01', periods=n_cases),
    })
    
    # Sample representation data
    n_reps = 800
    reps_assigned = pd.DataFrame({
        'IDNREPSASSIGNED': range(1, n_reps + 1),
        'IDNCASE': np.random.choice(juvenile_cases['IDNCASE'], n_reps),
        'STRATTYLEVEL': np.random.choice(['Pro Bono', 'Legal Aid', 'Private', 'None'], n_reps, p=[0.3, 0.3, 0.2, 0.2]),
        'STRATTYTYPE': np.random.choice(['Attorney', 'Accredited Rep', 'None'], n_reps, p=[0.6, 0.2, 0.2]),
    })
    
    return juvenile_cases, reps_assigned

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
    """Get overview statistics"""
    try:
        juvenile_cases, reps_assigned = load_real_data()
        
        # Calculate overview statistics
        total_cases = len(juvenile_cases)
        avg_age = juvenile_cases['AGE_AT_ENTRY'].mean()
        representation_rate = (len(reps_assigned[reps_assigned['STRATTYTYPE'] != 'None']) / total_cases) * 100
        
        # Top nationalities
        top_nationalities = juvenile_cases['NAT'].value_counts().head(5).to_dict()
        
        # Case outcomes by representation
        cases_with_rep = juvenile_cases[juvenile_cases['IDNCASE'].isin(
            reps_assigned[reps_assigned['STRATTYTYPE'] != 'None']['IDNCASE']
        )]
        
        overview_data = {
            "total_cases": int(total_cases),
            "average_age": round(float(avg_age), 1),
            "representation_rate": round(float(representation_rate), 1),
            "top_nationalities": top_nationalities,
            "demographic_breakdown": {
                "by_gender": juvenile_cases['Sex'].value_counts().to_dict(),
                "by_custody": juvenile_cases['CUSTODY'].value_counts().to_dict(),
                "by_case_type": juvenile_cases['CASE_TYPE'].value_counts().to_dict()
            },
            "trends": {
                "monthly_cases": juvenile_cases.groupby(
                    juvenile_cases['DATE_OF_ENTRY'].dt.to_period('M')
                ).size().tail(12).to_dict()
            }
        }
        
        return jsonify(overview_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Export for Vercel
def handler(request, context):
    """Vercel handler function"""
    return app(request.environ)

if __name__ == '__main__':
    app.run(debug=True)
