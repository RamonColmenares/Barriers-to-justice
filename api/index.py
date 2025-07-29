from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
import random

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['DEBUG'] = False

def generate_sample_data():
    """Generate sample data for demonstration"""
    random.seed(42)
    
    # Sample data without heavy dependencies
    nationalities = ['Mexico', 'Guatemala', 'El Salvador', 'Honduras', 'Other']
    languages = ['Spanish', 'English', 'Other']
    custody_types = ['Released', 'Detained']
    case_types = ['Removal', 'Asylum', 'Other']
    
    # Generate simple statistics
    total_cases = 1000
    sample_data = {
        'total_cases': total_cases,
        'nationalities': {
            'Mexico': 350,
            'Guatemala': 200,
            'El Salvador': 180,
            'Honduras': 150,
            'Other': 120
        },
        'languages': {
            'Spanish': 700,
            'English': 200,
            'Other': 100
        },
        'custody': {
            'Released': 600,
            'Detained': 400
        },
        'case_types': {
            'Removal': 500,
            'Asylum': 300,
            'Other': 200
        },
        'gender': {
            'M': 520,
            'F': 480
        },
        'representation': {
            'Pro Bono': 300,
            'Legal Aid': 300,
            'Private': 200,
            'None': 200
        }
    }
    
    return sample_data

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
        sample_data = generate_sample_data()
        
        # Calculate representation rate
        total_with_rep = (sample_data['representation']['Pro Bono'] + 
                         sample_data['representation']['Legal Aid'] + 
                         sample_data['representation']['Private'])
        representation_rate = (total_with_rep / sample_data['total_cases']) * 100
        
        overview_data = {
            "total_cases": sample_data['total_cases'],
            "average_age": 12.5,  # Static average for demo
            "representation_rate": round(representation_rate, 1),
            "top_nationalities": sample_data['nationalities'],
            "demographic_breakdown": {
                "by_gender": sample_data['gender'],
                "by_custody": sample_data['custody'],
                "by_case_type": sample_data['case_types']
            },
            "representation_breakdown": sample_data['representation'],
            "language_breakdown": sample_data['languages'],
            "trends": {
                "monthly_cases": {
                    "2024-01": 85,
                    "2024-02": 92,
                    "2024-03": 78,
                    "2024-04": 88,
                    "2024-05": 95,
                    "2024-06": 82,
                    "2024-07": 89,
                    "2024-08": 91,
                    "2024-09": 87,
                    "2024-10": 93,
                    "2024-11": 85,
                    "2024-12": 88
                }
            }
        }
        
        return jsonify(overview_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel serverless function handler
def handler(request, context):
    """Vercel handler function"""
    with app.app_context():
        return app.full_dispatch_request()

# For local development
if __name__ == '__main__':
    print("🚀 Starting development server...")
    print("🌐 Backend running on http://localhost:5000")
    print("📋 Available endpoints:")
    print("   GET /api/health")
    print("   GET /api/overview")
    app.run(debug=True, host='0.0.0.0', port=5000)
