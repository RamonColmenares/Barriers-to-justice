from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
from datetime import datetime
import json
from scipy import stats
import plotly.graph_objects as go
import plotly.express as px
# Remove sklearn imports for now to reduce cold start time
# from sklearn.linear_model import LogisticRegression
# from sklearn.model_selection import train_test_split
# from sklearn.metrics import accuracy_score, roc_auc_score

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
app.config['DEBUG'] = False

# Cache for data in memory (will reset on each cold start in Vercel)
_data_cache = {
    'juvenile_cases': None,
    'proceedings': None,
    'reps_assigned': None, 
    'lookup_decisions': None,
    'analysis_filtered': None,
    'data_loaded': False
}

def load_data():
    """Load and process compressed datasets like in the notebook"""
    global _data_cache
    
    if _data_cache['data_loaded']:
        return True
        
    try:
        print("Loading compressed datasets...")
        
        # Define paths to data files (in the api/data directory)
        base_path = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(base_path, "data")
        
        # Check if data directory exists
        if not os.path.exists(data_path):
            print(f"Data directory not found: {data_path}")
            # In production, try alternative paths
            possible_paths = [
                "/tmp/data",  # Vercel temp directory
                os.path.join(os.getcwd(), "data"),  # Current working directory
                "/var/task/data"  # Lambda/Vercel task directory
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    data_path = path
                    print(f"Using data path: {data_path}")
                    break
            else:
                print("No data directory found. Using fallback data.")
                return load_fallback_data()
        
        cases_path = os.path.join(data_path, "juvenile_cases_cleaned.csv.gz")
        proceedings_path = os.path.join(data_path, "juvenile_proceedings_cleaned.csv.gz")
        reps_assigned_path = os.path.join(data_path, "juvenile_reps_assigned.csv.gz")
        lookup_decision_path = os.path.join(data_path, "tblDecCode.csv")
        
        # Check if files exist
        required_files = [cases_path, proceedings_path, reps_assigned_path, lookup_decision_path]
        missing_files = [f for f in required_files if not os.path.exists(f)]
        
        if missing_files:
            print(f"Missing data files: {missing_files}")
            return load_fallback_data()
        
        # Load cases data with proper dtypes and date parsing
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
        
        _data_cache['juvenile_cases'] = pd.read_csv(
            filepath_or_buffer=cases_path,
            dtype=dtype,
            parse_dates=parse_dates,
            low_memory=False,
        )
        
        # Load reps_assigned data
        _data_cache['reps_assigned'] = pd.read_csv(
            filepath_or_buffer=reps_assigned_path,
            dtype={
                "IDNREPSASSIGNED": "Int64",
                "IDNCASE": "int64",
                "STRATTYLEVEL": "category",
                "STRATTYTYPE": "category",
            },
            compression="gzip",
            low_memory=False,
        )
        
        # Convert reps_assigned date columns to datetime
        _data_cache['reps_assigned']["E_28_DATE"] = pd.to_datetime(_data_cache['reps_assigned']["E_28_DATE"], errors="coerce")
        _data_cache['reps_assigned']["E_27_DATE"] = pd.to_datetime(_data_cache['reps_assigned']["E_27_DATE"], errors="coerce")
        
        # Load proceedings data
        _data_cache['proceedings'] = pd.read_csv(
            filepath_or_buffer=proceedings_path,
            dtype={
                "IDNPROCEEDING": "Int64",
                "IDNCASE": "Int64",
                "ABSENTIA": "category",
                "DEC_CODE": "category",
            },
            low_memory=False,
        )
        
        # Convert proceeding date columns to datetime
        date_cols = ["OSC_DATE", "INPUT_DATE", "COMP_DATE"]
        for col in date_cols:
            if col in _data_cache['proceedings'].columns:
                _data_cache['proceedings'][col] = pd.to_datetime(_data_cache['proceedings'][col], errors="coerce")
        
        # Load decision code lookup table
        _data_cache['lookup_decisions'] = pd.read_csv(
            filepath_or_buffer=lookup_decision_path,
            delimiter="\t",
            dtype={"DEC_CODE": "category"},
        )
        
        _data_cache['data_loaded'] = True
        print("Data loaded successfully!")
        
        # Process data for analysis (like in the notebook)
        process_analysis_data()
        
        return True
        
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        print("Falling back to sample data...")
        return load_fallback_data()

def load_fallback_data():
    """Load fallback sample data when real datasets are not available (for Vercel deployment)"""
    global _data_cache
    
    try:
        print("Loading fallback sample data...")
        
        # Create sample data that mimics the real structure
        sample_size = 1000
        
        # Sample cases data
        _data_cache['juvenile_cases'] = pd.DataFrame({
            'IDNCASE': range(1, sample_size + 1),
            'NAT': np.random.choice(['Mexico', 'Guatemala', 'El Salvador', 'Honduras', 'Other'], sample_size),
            'LANG': np.random.choice(['Spanish', 'English', 'Other'], sample_size),
            'CUSTODY': np.random.choice(['Released', 'Detained'], sample_size),
            'CASE_TYPE': np.random.choice(['Removal', 'Asylum', 'Other'], sample_size),
            'Sex': np.random.choice(['M', 'F'], sample_size),
            'LATEST_HEARING': pd.date_range('2018-01-01', '2025-01-01', periods=sample_size),
            'C_BIRTHDATE': pd.date_range('2005-01-01', '2015-01-01', periods=sample_size)
        })
        
        # Sample representation data with correct structure
        rep_cases = np.random.choice(range(1, sample_size + 1), sample_size // 2, replace=False)
        _data_cache['reps_assigned'] = pd.DataFrame({
            'IDNCASE': rep_cases,
            'STRATTYLEVEL': np.random.choice(['COURT', 'BOARD', 'A', 'B'], len(rep_cases)),
            'STRATTYTYPE': np.random.choice(['Pro Bono', 'Legal Aid', 'Private'], len(rep_cases))
        })
        
        # Sample proceedings data with correct decision codes from notebook
        decision_codes = ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W']
        _data_cache['proceedings'] = pd.DataFrame({
            'IDNCASE': range(1, sample_size + 1),
            'DEC_CODE': np.random.choice(decision_codes, sample_size),
            'COMP_DATE': pd.date_range('2018-01-01', '2025-01-01', periods=sample_size),
            'NAT': np.random.choice(['Mexico', 'Guatemala', 'El Salvador', 'Honduras'], sample_size),
            'LANG': np.random.choice(['Spanish', 'English'], sample_size),
            'CASE_TYPE': np.random.choice(['Removal', 'Asylum'], sample_size)
        })
        
        # Sample lookup data with correct structure from notebook
        _data_cache['lookup_decisions'] = pd.DataFrame({
            'strCode': ['A', 'C', 'G', 'R', 'S', 'T', 'D', 'E', 'V', 'X', 'O', 'W'],
            'strDescription': [
                'Asylum Granted', 'Continued', 'Granted Relief', 'Relief Granted', 
                'Special Immigration Juvenile Status', 'Terminated Favorably',
                'Denied', 'Entry of Appearance', 'Voluntary Departure', 'Dismissed',
                'Other', 'Withdrawn'
            ]
        })
        
        _data_cache['data_loaded'] = True
        print("Fallback data loaded successfully!")
        
        # Process sample data
        process_analysis_data()
        
        return True
        
    except Exception as e:
        print(f"Error loading fallback data: {str(e)}")
        return False

def process_analysis_data():
    """Process data for analysis exactly like in the notebook"""
    global _data_cache
    
    try:
        if (_data_cache['juvenile_cases'] is None or 
            _data_cache['proceedings'] is None or 
            _data_cache['reps_assigned'] is None or
            _data_cache['lookup_decisions'] is None):
            return False
            
        print("Processing analysis data exactly like notebook...")
        
        # Step 1: Merge proceedings with decision descriptions (like notebook)
        proceedings_with_decisions = _data_cache['proceedings'][
            ['IDNCASE', 'COMP_DATE', 'NAT', 'LANG', 'CASE_TYPE', 'DEC_CODE']
        ].merge(
            _data_cache['lookup_decisions'][['strCode', 'strDescription']],
            how='left',
            left_on='DEC_CODE',
            right_on='strCode'
        )
        
        # Drop strCode and rename strDescription (like notebook)
        proceedings_with_decisions = proceedings_with_decisions.drop(columns=['strCode'])
        proceedings_with_decisions = proceedings_with_decisions.rename(
            columns={'strDescription': 'decision_description'}
        )
        
        # Step 2: Merge juvenile_cases with proceedings_with_decisions (like notebook)
        merged_data = _data_cache['juvenile_cases'][
            ['IDNCASE', 'NAT', 'LANG', 'CASE_TYPE', 'Sex', 'C_BIRTHDATE', 'LATEST_HEARING']
        ].merge(
            proceedings_with_decisions[['IDNCASE', 'COMP_DATE', 'DEC_CODE', 'decision_description']],
            left_on='IDNCASE',
            right_on='IDNCASE',
            how='left'
        )
        
        # Step 3: Merge with reps_assigned (like notebook)
        merged_data = merged_data.merge(
            _data_cache['reps_assigned'][['IDNCASE', 'STRATTYLEVEL']], 
            on='IDNCASE', 
            how='left'
        )
        
        # Step 4: Fill missing STRATTYLEVEL values exactly like notebook
        merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].astype('category')
        if 'no_representation' not in merged_data['STRATTYLEVEL'].cat.categories:
            merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].cat.add_categories(['no_representation'])
        merged_data['STRATTYLEVEL'] = merged_data['STRATTYLEVEL'].fillna('no_representation')
        
        # Rename to REPRESENTATION_LEVEL (like notebook)
        merged_data = merged_data.rename(columns={'STRATTYLEVEL': 'REPRESENTATION_LEVEL'})
        
        # Step 5: Create hearing_date_combined exactly like notebook
        if merged_data['COMP_DATE'].dtype == 'object':
            merged_data['COMP_DATE'] = pd.to_datetime(merged_data['COMP_DATE'], errors='coerce')
        if merged_data['LATEST_HEARING'].dtype == 'object':
            merged_data['LATEST_HEARING'] = pd.to_datetime(merged_data['LATEST_HEARING'], errors='coerce')
            
        merged_data['hearing_date_combined'] = merged_data['COMP_DATE'].fillna(merged_data['LATEST_HEARING'])
        
        # Step 6: Determine policy era exactly like notebook
        def determine_policy_era(date):
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
        
        merged_data['POLICY_ERA'] = merged_data['hearing_date_combined'].apply(determine_policy_era)
        
        # Step 7: Create legal representation indicator exactly like notebook
        merged_data['HAS_LEGAL_REP'] = merged_data['REPRESENTATION_LEVEL'].apply(
            lambda x: "No Legal Representation"
            if x == "no_representation"
            else ("Has Legal Representation" if x == "COURT" or x == "BOARD" else "Unknown")
        )
        
        # Step 8: Create binary outcome classification exactly like notebook
        favorable_decisions = ["A", "C", "G", "R", "S", "T"]  # From notebook
        unfavorable_decisions = ["D", "E", "V", "X"]  # From notebook
        other_decisions = ["O", "W"]  # From notebook
        
        def categorize_outcome(DEC_CODE):
            if pd.isna(DEC_CODE):
                return "Unknown"
            elif DEC_CODE in favorable_decisions:
                return "Favorable" 
            elif DEC_CODE in unfavorable_decisions:
                return "Unfavorable"
            else:
                return "Other"
        
        merged_data['BINARY_OUTCOME'] = merged_data['DEC_CODE'].apply(categorize_outcome)
        merged_data['CASE_OUTCOME'] = merged_data['decision_description']
        
        # Step 9: Create analysis_filtered exactly like notebook
        analysis_filtered = merged_data[
            (merged_data['HAS_LEGAL_REP'] != "Unknown") &
            (merged_data['BINARY_OUTCOME'] != "Unknown") &
            (merged_data['BINARY_OUTCOME'] != "Other")
        ].copy()
        
        # Store processed data
        _data_cache['merged_data'] = merged_data
        _data_cache['analysis_filtered'] = analysis_filtered
        
        print(f"Analysis data processed successfully!")
        print(f"Total merged records: {len(merged_data):,}")
        print(f"Filtered analysis records: {len(analysis_filtered):,}")
        print(f"Legal representation distribution: {analysis_filtered['HAS_LEGAL_REP'].value_counts().to_dict()}")
        print(f"Outcome distribution: {analysis_filtered['BINARY_OUTCOME'].value_counts().to_dict()}")
        
        return True
        
    except Exception as e:
        print(f"Error processing analysis data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def get_data_statistics():
    """Calculate real statistics from the loaded data"""
    if not _data_cache['data_loaded'] or _data_cache['juvenile_cases'] is None:
        return None
    
    try:
        # Calculate basic statistics
        total_cases = len(_data_cache['juvenile_cases'])
        
        # Nationality distribution
        nat_counts = _data_cache['juvenile_cases']['NAT'].value_counts().head(10).to_dict()
        
        # Language distribution  
        lang_counts = _data_cache['juvenile_cases']['LANG'].value_counts().to_dict()
        
        # Custody distribution
        custody_counts = _data_cache['juvenile_cases']['CUSTODY'].value_counts().to_dict()
        
        # Case type distribution
        case_type_counts = _data_cache['juvenile_cases']['CASE_TYPE'].value_counts().to_dict()
        
        # Gender distribution
        gender_counts = _data_cache['juvenile_cases']['Sex'].value_counts().to_dict()
        
        # Calculate representation statistics
        rep_stats = {}
        if _data_cache['reps_assigned'] is not None:
            # Merge with reps data to get representation info
            cases_with_rep = _data_cache['juvenile_cases'].merge(_data_cache['reps_assigned'], on='IDNCASE', how='left')
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
        if 'C_BIRTHDATE' in _data_cache['juvenile_cases'].columns:
            current_date = pd.Timestamp.now()
            ages = (current_date - _data_cache['juvenile_cases']['C_BIRTHDATE']).dt.days / 365.25
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
        if _data_cache['juvenile_cases'] is not None and 'LATEST_HEARING' in _data_cache['juvenile_cases'].columns:
            try:
                # Group by month for trends
                monthly_data = _data_cache['juvenile_cases'].copy()
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

@app.route('/api/load-data')
def load_data_endpoint():
    """Endpoint to trigger data loading"""
    try:
        success = load_data()
        if success:
            return jsonify({
                "status": "success",
                "message": "Data loaded successfully",
                "cases_count": len(_data_cache['juvenile_cases']) if _data_cache['juvenile_cases'] is not None else 0,
                "proceedings_count": len(_data_cache['proceedings']) if _data_cache['proceedings'] is not None else 0,
                "reps_count": len(_data_cache['reps_assigned']) if _data_cache['reps_assigned'] is not None else 0
            })
        else:
            return jsonify({"error": "Failed to load data"}), 500
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/data-status')
def data_status():
    """Check if data is loaded and get basic info"""
    try:
        return jsonify({
            "data_loaded": _data_cache['data_loaded'],
            "cases_loaded": _data_cache['juvenile_cases'] is not None,
            "proceedings_loaded": _data_cache['proceedings'] is not None,
            "reps_loaded": _data_cache['reps_assigned'] is not None,
            "lookup_loaded": _data_cache['lookup_decisions'] is not None,
            "cases_count": len(_data_cache['juvenile_cases']) if _data_cache['juvenile_cases'] is not None else 0,
            "proceedings_count": len(_data_cache['proceedings']) if _data_cache['proceedings'] is not None else 0,
            "reps_count": len(_data_cache['reps_assigned']) if _data_cache['reps_assigned'] is not None else 0
        })
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/representation-outcomes')
def representation_outcomes():
    """Generate Plotly chart data for representation vs outcomes chart (exactly like notebook)"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Create crosstab for representation vs outcomes (like notebook)
        crosstab = pd.crosstab(
            _data_cache['analysis_filtered']['HAS_LEGAL_REP'], 
            _data_cache['analysis_filtered']['BINARY_OUTCOME']
        )
        
        # Calculate percentages (like notebook)
        percentage_data = pd.crosstab(
            _data_cache['analysis_filtered']['HAS_LEGAL_REP'],
            _data_cache['analysis_filtered']['BINARY_OUTCOME'], 
            normalize='index'
        ) * 100
        
        # Create Plotly figure exactly like notebook
        fig = go.Figure()
        
        # Add Favorable outcomes bar
        fig.add_trace(go.Bar(
            name='Favorable',
            x=crosstab.index,
            y=crosstab['Favorable'],
            marker_color='#10B981',
            text=[f"{p:.1f}%" for p in percentage_data['Favorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Add Unfavorable outcomes bar
        fig.add_trace(go.Bar(
            name='Unfavorable',
            x=crosstab.index,
            y=crosstab['Unfavorable'],
            marker_color='#EF4444',
            text=[f"{p:.1f}%" for p in percentage_data['Unfavorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Update layout to match notebook style
        fig.update_layout(
            title={
                'text': 'Case Outcomes by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            barmode='stack',
            xaxis={
                'title': 'Legal Representation',
                'tickangle': 0,
                'title_font': {'size': 14}
            },
            yaxis={
                'title': 'Count',
                'type': 'log',  # Log scale like in notebook
                'title_font': {'size': 14}
            },
            showlegend=True,
            legend=dict(
                title='Case Outcome',
                orientation='v',
                x=1.05,
                y=1
            ),
            margin=dict(t=60, l=60, r=30, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif'),
            width=800,
            height=500
        )
        
        # Convert to JSON format for frontend
        chart_data = {
            'data': fig.data,
            'layout': fig.layout,
            'config': {
                'responsive': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'displaylogo': False
            }
        }
        
        # Convert to JSON-serializable format
        import plotly.utils
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/time-series')
def time_series_analysis():
    """Generate Plotly time series chart exactly like notebook"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Filter data with valid dates from 2016 onwards (like notebook)
        date_valid = ~_data_cache['analysis_filtered']['LATEST_HEARING'].isna()
        time_series_df = _data_cache['analysis_filtered'][date_valid].copy()
        
        start_date = pd.Timestamp("2016-01-01")
        current_date = pd.Timestamp.now()
        recent_data = time_series_df[
            (time_series_df['LATEST_HEARING'] >= start_date) & 
            (time_series_df['LATEST_HEARING'] <= current_date)
        ]
        
        # Create quarterly data (like notebook)
        recent_data['YEAR_QUARTER'] = recent_data['LATEST_HEARING'].dt.to_period('Q')
        
        quarterly_rep = recent_data.groupby('YEAR_QUARTER').agg(
            total_cases=('HAS_LEGAL_REP', 'count'),
            represented_cases=('HAS_LEGAL_REP', lambda x: (x == 'Has Legal Representation').sum())
        )
        quarterly_rep['representation_rate'] = quarterly_rep['represented_cases'] / quarterly_rep['total_cases']
        
        # Convert to timestamp for plotting
        quarterly_rep['date'] = quarterly_rep.index.to_timestamp()
        
        # Create Plotly figure exactly like notebook
        fig = go.Figure()
        
        # Add main time series line (like notebook)
        fig.add_trace(go.Scatter(
            x=quarterly_rep['date'],
            y=quarterly_rep['representation_rate'],
            mode='lines+markers',
            name='Representation Rate',
            line=dict(color='navy', width=2),
            marker=dict(size=6, color='navy'),
            opacity=0.7
        ))
        
        # Add administration change lines (like notebook)
        admin_changes = [
            (pd.Timestamp("2017-01-20"), "Trump Administration"),
            (pd.Timestamp("2021-01-20"), "Biden Administration"),
            (pd.Timestamp("2025-01-20"), "Trump Administration II")
        ]
        
        shapes = []
        annotations = []
        
        for date, label in admin_changes:
            # Add vertical line
            shapes.append(dict(
                type="line",
                x0=date, x1=date,
                y0=0, y1=1,
                line=dict(color="red", dash="dash", width=2),
                opacity=0.6
            ))
            
            # Add label annotation
            annotations.append(dict(
                x=date,
                y=0.95,
                text=label,
                showarrow=False,
                textangle=-90,
                xanchor="right",
                yanchor="top",
                font=dict(size=10, color="red")
            ))
        
        # Update layout to match notebook exactly
        fig.update_layout(
            title={
                'text': 'Legal Representation Rate for Juvenile Immigration Cases (2016-2025)',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            xaxis={
                'title': 'Year',
                'title_font': {'size': 14},
                'tickformat': '%Y',
                'dtick': 'M12'  # Show every year
            },
            yaxis={
                'title': 'Representation Rate',
                'title_font': {'size': 14},
                'range': [0, 1],
                'tickformat': '.0%'
            },
            shapes=shapes,
            annotations=annotations,
            showlegend=False,
            margin=dict(t=60, l=60, r=30, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif'),
            width=1000,
            height=500
        )
        
        # Add grid (like notebook)
        
        # Convert to JSON format
        chart_data = {
            'data': fig.data,
            'layout': fig.layout,
            'config': {
                'responsive': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'displaylogo': False
            }
        }
        
        import plotly.utils
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/chi-square')
def chi_square_analysis():
    """Generate chi-square analysis results (like notebook)"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        results = {}
        
        # Chi-square test for representation by policy era
        era_rep_table = pd.crosstab(
            _data_cache['analysis_filtered']['POLICY_ERA'], 
            _data_cache['analysis_filtered']['HAS_LEGAL_REP']
        )
        chi2_era, p_era, dof_era, _ = stats.chi2_contingency(era_rep_table)
        n_era = era_rep_table.values.sum()
        cramer_v_era = np.sqrt(chi2_era / (n_era * (min(era_rep_table.shape) - 1)))
        
        results['representation_by_era'] = {
            'chi_square': round(float(chi2_era), 2),
            'p_value': float(p_era),
            'degrees_of_freedom': int(dof_era),
            'cramer_v': round(float(cramer_v_era), 3),
            'significant': bool(p_era < 0.05),
            'contingency_table': era_rep_table.to_dict()
        }
        
        # Chi-square test for outcomes by representation
        outcome_rep_table = pd.crosstab(
            _data_cache['analysis_filtered']['BINARY_OUTCOME'],
            _data_cache['analysis_filtered']['HAS_LEGAL_REP']
        )
        chi2_outcome, p_outcome, dof_outcome, _ = stats.chi2_contingency(outcome_rep_table)
        n_outcome = outcome_rep_table.values.sum()
        cramer_v_outcome = np.sqrt(chi2_outcome / (n_outcome * (min(outcome_rep_table.shape) - 1)))
        
        # Calculate odds ratio
        try:
            a = outcome_rep_table.loc['Favorable', 'Has Legal Representation']
            b = outcome_rep_table.loc['Unfavorable', 'Has Legal Representation'] 
            c = outcome_rep_table.loc['Favorable', 'No Legal Representation']
            d = outcome_rep_table.loc['Unfavorable', 'No Legal Representation']
            
            odds_with_rep = a / b if b > 0 else 0
            odds_without_rep = c / d if d > 0 else 0
            odds_ratio = odds_with_rep / odds_without_rep if odds_without_rep > 0 else 0
        except:
            odds_ratio = 0
        
        results['outcomes_by_representation'] = {
            'chi_square': round(float(chi2_outcome), 2),
            'p_value': float(p_outcome),
            'degrees_of_freedom': int(dof_outcome),
            'cramer_v': round(float(cramer_v_outcome), 3),
            'significant': bool(p_outcome < 0.05),
            'odds_ratio': round(float(odds_ratio), 3),
            'contingency_table': outcome_rep_table.to_dict()
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/api/findings/outcome-percentages')
def outcome_percentages_chart():
    """Generate the percentage breakdown chart exactly like notebook"""
    try:
        if not load_data() or _data_cache['analysis_filtered'] is None:
            return jsonify({"error": "Failed to load or process data"}), 500
        
        # Calculate percentages correctly (like notebook)
        percentage_data = pd.crosstab(
            _data_cache['analysis_filtered']['HAS_LEGAL_REP'],
            _data_cache['analysis_filtered']['BINARY_OUTCOME'],
            normalize='index'
        ) * 100
        
        # Create stacked bar chart with percentages (like notebook)
        fig = go.Figure()
        
        # Add Favorable outcomes
        fig.add_trace(go.Bar(
            name='Favorable',
            x=percentage_data.index,
            y=percentage_data['Favorable'],
            marker_color='#10B981',
            text=[f"{p:.1f}%" for p in percentage_data['Favorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Add Unfavorable outcomes  
        fig.add_trace(go.Bar(
            name='Unfavorable',
            x=percentage_data.index,
            y=percentage_data['Unfavorable'],
            marker_color='#EF4444',
            text=[f"{p:.1f}%" for p in percentage_data['Unfavorable']],
            textposition='inside',
            textfont=dict(color='white', size=12)
        ))
        
        # Update layout to match notebook
        fig.update_layout(
            title={
                'text': 'Case Outcome Percentages by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            barmode='stack',
            xaxis={
                'title': 'Legal Representation',
                'tickangle': 0,
                'title_font': {'size': 14}
            },
            yaxis={
                'title': 'Percentage (%)',
                'title_font': {'size': 14},
                'range': [0, 100]
            },
            showlegend=True,
            legend=dict(
                title='Case Outcome',
                orientation='v',
                x=1.05,
                y=1
            ),
            margin=dict(t=60, l=60, r=30, b=80),
            plot_bgcolor='white',
            paper_bgcolor='white',
            font=dict(family='Arial, sans-serif'),
            width=800,
            height=500
        )
        
        
        # Convert to JSON
        chart_data = {
            'data': fig.data,
            'layout': fig.layout,
            'config': {
                'responsive': True,
                'displayModeBar': True,
                'modeBarButtonsToRemove': ['pan2d', 'lasso2d', 'select2d'],
                'displaylogo': False
            }
        }
        
        import plotly.utils
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

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
    print("   GET /api/load-data")
    print("   GET /api/data-status")
    print("   GET /api/findings/representation-outcomes")
    print("   GET /api/findings/time-series")
    print("   GET /api/findings/chi-square")
    app.run(debug=True, host='0.0.0.0', port=5000)
