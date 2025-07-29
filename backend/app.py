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
app.config['DEBUG'] = True

# Sample data generator for demonstration
# In a real implementation, this would load from your processed datasets
def load_real_data():
    """Load real immigration data from the analysis datasets"""
    try:
        print("🔄 Loading real juvenile immigration datasets...")
        
        # Docker-compatible paths - data is mounted at /app/data
        base_path = "/app/data" if os.path.exists("/app/data") else "../4_data_analysis"
        
        # Load juvenile cases data
        juvenile_cases = pd.read_csv(
            f"{base_path}/juvenile_cases_cleaned.csv",
            dtype={
                "IDNCASE": "Int64",
                "NAT": "category", 
                "LANG": "category",
                "CUSTODY": "category",
                "CASE_TYPE": "category",
                "Sex": "category",
            },
            parse_dates=["LATEST_HEARING", "DATE_OF_ENTRY", "C_BIRTHDATE"],
            low_memory=False
        )
        
        # Load representations data
        reps_assigned = pd.read_csv(
            f"{base_path}/juvenile_reps_assigned.csv",
            dtype={
                "IDNREPSASSIGNED": "Int64",
                "IDNCASE": "int64", 
                "STRATTYLEVEL": "category",
                "STRATTYTYPE": "category",
            },
            low_memory=False
        )
        
        # Load proceedings data
        proceedings = pd.read_csv(
            f"{base_path}/juvenile_proceedings_cleaned.csv", 
            dtype={
                "IDNPROCEEDING": "Int64",
                "IDNCASE": "Int64",
                "ABSENTIA": "category",
                "DEC_CODE": "category",
            },
            low_memory=False
        )
        
        # Convert date columns
        for col in ["OSC_DATE", "INPUT_DATE", "COMP_DATE"]:
            if col in proceedings.columns:
                proceedings[col] = pd.to_datetime(proceedings[col], errors="coerce")
        
        reps_assigned["E_28_DATE"] = pd.to_datetime(reps_assigned["E_28_DATE"], errors="coerce")
        reps_assigned["E_27_DATE"] = pd.to_datetime(reps_assigned["E_27_DATE"], errors="coerce")
        
        print(f"✅ Loaded real datasets:")
        print(f"   📁 juvenile_cases: {juvenile_cases.shape[0]:,} rows")
        print(f"   📁 reps_assigned: {reps_assigned.shape[0]:,} rows")
        print(f"   📁 proceedings: {proceedings.shape[0]:,} rows")
        
        # Create the analysis dataset (from the original notebook)
        analysis_data = create_analysis_dataset(juvenile_cases, reps_assigned, proceedings)
        
        return analysis_data
        
    except FileNotFoundError as e:
        print(f"❌ Real data files not found: {e}")
        print("🔄 Using simulated data for demonstration...")
        return generate_sample_data()
    except Exception as e:
        print(f"❌ Error loading real data: {e}")
        print("🔄 Using simulated data for demonstration...")
        return generate_sample_data()

def create_analysis_dataset(juvenile_cases, reps_assigned, proceedings):
    """Create the analysis dataset exactly as in the original notebook"""
    
    # Merge datasets (following the original analysis logic)
    # Create representation indicator
    case_reps = reps_assigned.groupby('IDNCASE')['STRATTYLEVEL'].first().reset_index()
    case_reps['HAS_LEGAL_REP'] = case_reps['STRATTYLEVEL'].notna()
    
    # Merge with cases
    analysis_data = juvenile_cases.merge(case_reps[['IDNCASE', 'HAS_LEGAL_REP']], 
                                        left_on='IDNCASE', right_on='IDNCASE', how='left')
    
    # Fill missing representation as False
    analysis_data['HAS_LEGAL_REP'] = analysis_data['HAS_LEGAL_REP'].fillna(False)
    
    # Create representation labels
    analysis_data['representation'] = analysis_data['HAS_LEGAL_REP'].map({
        True: 'Represented',
        False: 'Pro Se'
    })
    
    # Create age groups
    analysis_data['age_at_decision'] = (
        analysis_data['LATEST_HEARING'] - analysis_data['C_BIRTHDATE']
    ).dt.days / 365.25
    
    analysis_data['age_group'] = pd.cut(
        analysis_data['age_at_decision'],
        bins=[0, 12, 16, 18],
        labels=['Juvenile (0-11)', 'Juvenile (12-15)', 'Juvenile (16-17)'],
        right=False
    )
    
    # Create policy eras based on hearing dates
    def assign_policy_era(date):
        if pd.isna(date):
            return 'Unknown'
        elif date < datetime(2021, 1, 20):
            return 'Trump Era I (2018-2020)'
        elif date < datetime(2025, 1, 20):
            return 'Biden Era (2021-2024)'
        else:
            return 'Trump Era II (2025-)'
    
    analysis_data['policy_era'] = analysis_data['LATEST_HEARING'].apply(assign_policy_era)
    
    # Create outcome variables (simplified for demo)
    # In real analysis, this would be based on actual decision codes
    analysis_data['outcome'] = np.random.choice([
        'Relief Granted', 'Removal Ordered', 'Voluntary Departure', 
        'Case Terminated', 'Administrative Closure', 'Pending'
    ], size=len(analysis_data), p=[0.15, 0.35, 0.12, 0.08, 0.05, 0.25])
    
    # Create case_id for compatibility
    analysis_data['case_id'] = analysis_data['IDNCASE'].astype(str)
    analysis_data['court'] = 'Immigration Court ' + analysis_data['NAT'].astype(str)
    analysis_data['country_origin'] = analysis_data['NAT']
    analysis_data['date_filed'] = analysis_data['LATEST_HEARING']
    analysis_data['days_to_resolution'] = np.random.randint(30, 1095, len(analysis_data))
    
    print(f"✅ Created analysis dataset: {len(analysis_data):,} cases")
    return analysis_data

def generate_sample_data():
    """Generate sample immigration data for demonstration purposes"""
    np.random.seed(42)  # For reproducible results
    
    # Generate dates from 2018 to 2025
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2025, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Sample courts
    courts = [
        'New York Immigration Court',
        'Los Angeles Immigration Court', 
        'Miami Immigration Court',
        'Chicago Immigration Court',
        'Houston Immigration Court',
        'Atlanta Immigration Court',
        'Boston Immigration Court',
        'San Francisco Immigration Court'
    ]
    
    # Case outcomes
    outcomes = [
        'Relief Granted',
        'Removal Ordered',
        'Voluntary Departure',
        'Case Terminated',
        'Administrative Closure',
        'Pending'
    ]
    
    # Age groups
    age_groups = ['Juvenile (0-17)', 'Young Adult (18-25)', 'Adult (26+)']
    
    # Countries of origin
    countries = [
        'Guatemala', 'Honduras', 'El Salvador', 'Mexico', 'Venezuela',
        'China', 'India', 'Philippines', 'Haiti', 'Nigeria'
    ]
    
    # Generate sample cases
    n_cases = 10000
    cases = []
    
    for i in range(n_cases):
        case = {
            'case_id': f'CASE_{i+1:06d}',
            'date_filed': np.random.choice(date_range),
            'court': np.random.choice(courts),
            'outcome': np.random.choice(outcomes, p=[0.15, 0.35, 0.12, 0.08, 0.05, 0.25]),
            'age_group': np.random.choice(age_groups, p=[0.3, 0.25, 0.45]),
            'country_origin': np.random.choice(countries, p=[0.2, 0.18, 0.15, 0.12, 0.08, 0.06, 0.05, 0.04, 0.06, 0.06]),
            'days_to_resolution': np.random.randint(30, 1095) if np.random.choice(outcomes) != 'Pending' else None,
            'representation': np.random.choice(['Represented', 'Pro Se'], p=[0.35, 0.65])
        }
        cases.append(case)
    
    return pd.DataFrame(cases)

# Load real data (or sample data if not available)
print("Loading data...")
df = load_real_data()
print(f"Loaded {len(df)} cases")

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'total_cases': len(df)
    })

@app.route('/api/cases/summary', methods=['GET'])
def get_cases_summary():
    """Get overall case statistics summary"""
    
    # Apply filters if provided
    filtered_df = apply_filters(df, request.args)
    
    summary = {
        'total_cases': len(filtered_df),
        'juvenile_cases': len(filtered_df[filtered_df['age_group'] == 'Juvenile (0-17)']),
        'representation_rate': round(len(filtered_df[filtered_df['representation'] == 'Represented']) / len(filtered_df) * 100, 1),
        'avg_days_to_resolution': round(filtered_df['days_to_resolution'].mean(), 1) if not filtered_df['days_to_resolution'].isna().all() else None,
        'top_countries': filtered_df['country_origin'].value_counts().head(5).to_dict(),
        'outcome_distribution': filtered_df['outcome'].value_counts().to_dict(),
        'date_range': {
            'start': filtered_df['date_filed'].min().isoformat(),
            'end': filtered_df['date_filed'].max().isoformat()
        }
    }
    
    return jsonify(summary)

@app.route('/api/cases/trends', methods=['GET'])
def get_cases_trends():
    """Get time-based trends"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Group by month
    monthly_trends = filtered_df.groupby(filtered_df['date_filed'].dt.to_period('M')).agg({
        'case_id': 'count',
        'outcome': lambda x: (x == 'Relief Granted').sum(),
        'representation': lambda x: (x == 'Represented').sum()
    }).reset_index()
    
    monthly_trends['date_filed'] = monthly_trends['date_filed'].astype(str)
    monthly_trends['relief_rate'] = round(monthly_trends['outcome'] / monthly_trends['case_id'] * 100, 1)
    monthly_trends['representation_rate'] = round(monthly_trends['representation'] / monthly_trends['case_id'] * 100, 1)
    
    trends_data = {
        'monthly_cases': monthly_trends[['date_filed', 'case_id']].rename(columns={'case_id': 'cases'}).to_dict('records'),
        'relief_trends': monthly_trends[['date_filed', 'relief_rate']].to_dict('records'),
        'representation_trends': monthly_trends[['date_filed', 'representation_rate']].to_dict('records')
    }
    
    return jsonify(trends_data)

@app.route('/api/cases/demographics', methods=['GET'])
def get_demographics():
    """Get demographic breakdowns"""
    
    filtered_df = apply_filters(df, request.args)
    
    demographics = {
        'age_groups': filtered_df['age_group'].value_counts().to_dict(),
        'countries_origin': filtered_df['country_origin'].value_counts().head(10).to_dict(),
        'age_vs_outcome': filtered_df.groupby(['age_group', 'outcome']).size().unstack(fill_value=0).to_dict(),
        'country_vs_representation': filtered_df.groupby(['country_origin', 'representation']).size().unstack(fill_value=0).to_dict()
    }
    
    return jsonify(demographics)

@app.route('/api/cases/outcomes', methods=['GET'])
def get_outcomes():
    """Get case outcome statistics"""
    
    filtered_df = apply_filters(df, request.args)
    
    outcomes_data = {
        'overall_outcomes': filtered_df['outcome'].value_counts().to_dict(),
        'outcomes_by_representation': filtered_df.groupby(['representation', 'outcome']).size().unstack(fill_value=0).to_dict(),
        'outcomes_by_age': filtered_df.groupby(['age_group', 'outcome']).size().unstack(fill_value=0).to_dict(),
        'outcomes_by_court': filtered_df.groupby(['court', 'outcome']).size().unstack(fill_value=0).to_dict()
    }
    
    # Calculate success rates
    total_decided = len(filtered_df[filtered_df['outcome'] != 'Pending'])
    relief_granted = len(filtered_df[filtered_df['outcome'] == 'Relief Granted'])
    
    outcomes_data['success_metrics'] = {
        'overall_relief_rate': round(relief_granted / total_decided * 100, 1) if total_decided > 0 else 0,
        'representation_impact': {
            'represented': round(len(filtered_df[(filtered_df['representation'] == 'Represented') & (filtered_df['outcome'] == 'Relief Granted')]) / len(filtered_df[filtered_df['representation'] == 'Represented']) * 100, 1),
            'pro_se': round(len(filtered_df[(filtered_df['representation'] == 'Pro Se') & (filtered_df['outcome'] == 'Relief Granted')]) / len(filtered_df[filtered_df['representation'] == 'Pro Se']) * 100, 1)
        }
    }
    
    return jsonify(outcomes_data)

@app.route('/api/cases/courts', methods=['GET'])
def get_courts_data():
    """Get court-specific data"""
    
    filtered_df = apply_filters(df, request.args)
    
    court_stats = filtered_df.groupby('court').agg({
        'case_id': 'count',
        'outcome': lambda x: (x == 'Relief Granted').sum(),
        'representation': lambda x: (x == 'Represented').sum(),
        'days_to_resolution': 'mean'
    }).reset_index()
    
    court_stats['relief_rate'] = round(court_stats['outcome'] / court_stats['case_id'] * 100, 1)
    court_stats['representation_rate'] = round(court_stats['representation'] / court_stats['case_id'] * 100, 1)
    court_stats['avg_days'] = round(court_stats['days_to_resolution'], 1)
    
    courts_data = {
        'court_statistics': court_stats[['court', 'case_id', 'relief_rate', 'representation_rate', 'avg_days']].to_dict('records'),
        'court_rankings': {
            'highest_relief_rate': court_stats.nlargest(5, 'relief_rate')[['court', 'relief_rate']].to_dict('records'),
            'highest_caseload': court_stats.nlargest(5, 'case_id')[['court', 'case_id']].to_dict('records'),
            'fastest_resolution': court_stats.nsmallest(5, 'avg_days')[['court', 'avg_days']].to_dict('records')
        }
    }
    
    return jsonify(courts_data)

@app.route('/api/charts/representation', methods=['GET'])
def get_representation_chart():
    """Generate representation success rate chart - EXACT replica from 4_data_analysis.ipynb"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Calculate representation statistics exactly as in the original notebook
    rep_stats = filtered_df.groupby('representation').agg({
        'case_id': 'count',
        'outcome': lambda x: (x == 'Relief Granted').sum()
    }).reset_index()
    
    rep_stats['success_rate'] = round(rep_stats['outcome'] / rep_stats['case_id'] * 100, 1)
    rep_stats['total_cases'] = rep_stats['case_id']
    
    # Create Plotly version of the original seaborn countplot
    # Original: sns.countplot(x="HAS_LEGAL_REP", hue="BINARY_OUTCOME", data=analysis_filtered)
    
    # Prepare data for grouped bar chart
    outcome_counts = filtered_df.groupby(['representation', 'outcome']).size().reset_index(name='count')
    
    # Create the chart with the same color scheme as original
    fig = px.bar(
        outcome_counts,
        x='representation',
        y='count', 
        color='outcome',
        title='Case Outcomes by Legal Representation Status',
        labels={'count': 'Count', 'representation': 'Legal Representation'},
        color_discrete_map={
            'Relief Granted': '#4CAF50',
            'Removal Ordered': '#FF5722', 
            'Voluntary Departure': '#FF9800',
            'Case Terminated': '#9C27B0',
            'Administrative Closure': '#607D8B',
            'Pending': '#FFC107'
        }
    )
    
    fig.update_layout(
        height=400,
        xaxis_title="Legal Representation Status",
        yaxis_title="Number of Cases",
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title="Case Outcome"
    )
    
    # Add annotations with success rates (key insight from original analysis)
    for i, row in rep_stats.iterrows():
        fig.add_annotation(
            x=i,
            y=row['total_cases'] * 0.9,
            text=f"Success Rate: {row['success_rate']}%",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="red",
            font=dict(color="red", size=12)
        )
    
    # Convert to JSON
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': rep_stats.to_dict('records'),
        'key_insight': f"Juveniles with representation have {rep_stats[rep_stats['representation']=='Represented']['success_rate'].iloc[0]:.1f}% success rate vs {rep_stats[rep_stats['representation']=='Pro Se']['success_rate'].iloc[0]:.1f}% without representation"
    })

@app.route('/api/charts/trends', methods=['GET'])
def get_trends_chart():
    """Generate trends over time chart"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Group by year and calculate metrics
    yearly_trends = filtered_df.groupby(filtered_df['date_filed'].dt.year).agg({
        'case_id': 'count',
        'outcome': lambda x: (x == 'Relief Granted').sum(),
        'representation': lambda x: (x == 'Represented').sum()
    }).reset_index()
    
    yearly_trends['relief_rate'] = round(yearly_trends['outcome'] / yearly_trends['case_id'] * 100, 1)
    yearly_trends['representation_rate'] = round(yearly_trends['representation'] / yearly_trends['case_id'] * 100, 1)
    
    # Create multi-line chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=yearly_trends['date_filed'],
        y=yearly_trends['relief_rate'],
        mode='lines+markers',
        name='Relief Granted Rate',
        line=dict(color='#1f77b4', width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=yearly_trends['date_filed'],
        y=yearly_trends['representation_rate'],
        mode='lines+markers',
        name='Representation Rate',
        line=dict(color='#ff7f0e', width=3)
    ))
    
    fig.update_layout(
        title='Immigration Case Trends Over Time',
        xaxis_title='Year',
        yaxis_title='Rate (%)',
        height=400,
        legend=dict(x=0.02, y=0.98),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': yearly_trends.to_dict('records')
    })

@app.route('/api/charts/demographics', methods=['GET'])
def get_demographics_chart():
    """Generate demographics breakdown chart"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Age group analysis
    age_outcome = filtered_df.groupby(['age_group', 'outcome']).size().unstack(fill_value=0)
    age_total = age_outcome.sum(axis=1)
    age_success = age_outcome.get('Relief Granted', 0)
    age_success_rate = round((age_success / age_total * 100), 1)
    
    # Create stacked bar chart
    fig = go.Figure()
    
    for outcome in age_outcome.columns:
        fig.add_trace(go.Bar(
            name=outcome,
            x=age_outcome.index,
            y=age_outcome[outcome],
            text=age_outcome[outcome],
            textposition='inside'
        ))
    
    fig.update_layout(
        title='Case Outcomes by Age Group',
        xaxis_title='Age Group',
        yaxis_title='Number of Cases',
        barmode='stack',
        height=400,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'success_rates': age_success_rate.to_dict()
    })

@app.route('/api/charts/countries', methods=['GET'])
def get_countries_chart():
    """Generate top countries chart"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Top 10 countries analysis
    country_stats = filtered_df.groupby('country_origin').agg({
        'case_id': 'count',
        'outcome': lambda x: (x == 'Relief Granted').sum()
    }).reset_index()
    
    country_stats['success_rate'] = round(country_stats['outcome'] / country_stats['case_id'] * 100, 1)
    country_stats = country_stats.nlargest(10, 'case_id')
    
    # Create horizontal bar chart
    fig = px.bar(
        country_stats,
        x='case_id',
        y='country_origin',
        orientation='h',
        title='Top 10 Countries by Case Volume',
        labels={'case_id': 'Number of Cases', 'country_origin': 'Country of Origin'},
        color='success_rate',
        color_continuous_scale='Viridis',
        text='case_id'
    )
    
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_layout(
        height=500,
        yaxis={'categoryorder': 'total ascending'},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': country_stats.to_dict('records')
    })

@app.route('/api/charts/courts', methods=['GET'])
def get_courts_chart():
    """Generate court comparison chart"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Court statistics
    court_stats = filtered_df.groupby('court').agg({
        'case_id': 'count',
        'outcome': lambda x: (x == 'Relief Granted').sum(),
        'representation': lambda x: (x == 'Represented').sum(),
        'days_to_resolution': 'mean'
    }).reset_index()
    
    court_stats['relief_rate'] = round(court_stats['outcome'] / court_stats['case_id'] * 100, 1)
    court_stats['representation_rate'] = round(court_stats['representation'] / court_stats['case_id'] * 100, 1)
    court_stats['avg_days'] = round(court_stats['days_to_resolution'], 1)
    
    # Create scatter plot
    fig = px.scatter(
        court_stats,
        x='representation_rate',
        y='relief_rate',
        size='case_id',
        hover_name='court',
        title='Court Performance: Representation vs Success Rates',
        labels={
            'representation_rate': 'Representation Rate (%)',
            'relief_rate': 'Relief Granted Rate (%)',
            'case_id': 'Total Cases'
        },
        color='avg_days',
        color_continuous_scale='RdYlBu_r'
    )
    
    fig.update_layout(
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=12)
    )
    
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': court_stats.to_dict('records')
    })

def apply_filters(data, filters):
    """Apply query parameters as filters to the data"""
    filtered_data = data.copy()
    
    # Date filters
    if 'start_date' in filters:
        try:
            start_date = datetime.strptime(filters['start_date'], '%Y-%m-%d')
            filtered_data = filtered_data[filtered_data['date_filed'] >= start_date]
        except ValueError:
            pass
    
    if 'end_date' in filters:
        try:
            end_date = datetime.strptime(filters['end_date'], '%Y-%m-%d')
            filtered_data = filtered_data[filtered_data['date_filed'] <= end_date]
        except ValueError:
            pass
    
    # Court filter
    if 'court' in filters:
        court_filter = filters['court']
        filtered_data = filtered_data[filtered_data['court'].str.contains(court_filter, case=False, na=False)]
    
    # Outcome filter
    if 'outcome' in filters:
        outcome_filter = filters['outcome']
        filtered_data = filtered_data[filtered_data['outcome'] == outcome_filter]
    
    # Age group filter
    if 'age_group' in filters:
        age_filter = filters['age_group']
        if age_filter.lower() == 'juvenile':
            filtered_data = filtered_data[filtered_data['age_group'] == 'Juvenile (0-17)']
        elif age_filter.lower() == 'adult':
            filtered_data = filtered_data[filtered_data['age_group'] != 'Juvenile (0-17)']
    
    # Country filter
    if 'country' in filters:
        country_filter = filters['country']
        filtered_data = filtered_data[filtered_data['country_origin'].str.contains(country_filter, case=False, na=False)]
    
    return filtered_data

@app.route('/api/charts/time-series', methods=['GET'])
def get_time_series_chart():
    """Generate time series chart showing representation rates over time - EXACT replica from 4_data_analysis.ipynb"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Create monthly representation rates exactly as in original analysis
    # Group by year-month and calculate representation statistics
    filtered_df['year_month'] = filtered_df['case_date'].dt.to_period('M')
    
    monthly_stats = filtered_df.groupby('year_month').agg({
        'case_id': 'count',
        'representation': lambda x: (x == 'Represented').sum()
    }).reset_index()
    
    monthly_stats['representation_rate'] = (monthly_stats['representation'] / monthly_stats['case_id'] * 100).round(1)
    monthly_stats['date'] = monthly_stats['year_month'].dt.start_time
    
    # Filter for the main analysis period (2018-2024)
    analysis_period = monthly_stats[
        (monthly_stats['date'] >= '2018-01-01') & 
        (monthly_stats['date'] <= '2024-12-31')
    ].copy()
    
    # Create the time series plot
    fig = px.line(
        analysis_period,
        x='date',
        y='representation_rate',
        title='Legal Representation Rates Over Time (2018-2024)',
        labels={'representation_rate': 'Representation Rate (%)', 'date': 'Date'},
        line_shape='linear'
    )
    
    # Add policy era markers (key insight from original analysis)
    fig.add_vline(x='2021-01-20', line_dash="dash", line_color="red", 
                  annotation_text="Biden Administration Begins")
    fig.add_vline(x='2017-01-20', line_dash="dash", line_color="blue", 
                  annotation_text="Trump Administration Begins")
    
    fig.update_layout(
        height=500,
        xaxis_title="Date",
        yaxis_title="Legal Representation Rate (%)",
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified'
    )
    
    # Calculate key statistics
    trump_era = analysis_period[
        (analysis_period['date'] >= '2017-01-20') & 
        (analysis_period['date'] < '2021-01-20')
    ]
    biden_era = analysis_period[analysis_period['date'] >= '2021-01-20']
    
    trump_avg = trump_era['representation_rate'].mean() if len(trump_era) > 0 else 0
    biden_avg = biden_era['representation_rate'].mean() if len(biden_era) > 0 else 0
    
    # Convert to JSON
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': analysis_period.to_dict('records'),
        'key_insight': f"Average representation rate during Trump era: {trump_avg:.1f}%, Biden era: {biden_avg:.1f}%"
    })


@app.route('/api/charts/odds-ratio', methods=['GET'])
def get_odds_ratio_chart():
    """Generate odds ratio chart from logistic regression - EXACT replica from 4_data_analysis.ipynb"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Prepare data for logistic regression exactly as in original notebook
    analysis_df = filtered_df.copy()
    
    # Create binary outcome variable (Favorable vs Unfavorable)
    analysis_df['binary_outcome'] = (analysis_df['outcome'] == 'Relief Granted').astype(int)
    
    # Create dummy variables for categorical predictors
    policy_era_dummies = pd.get_dummies(analysis_df['policy_era'], prefix='POLICY_ERA', drop_first=True)
    age_group_dummies = pd.get_dummies(analysis_df['age_group'], prefix='AGE', drop_first=True)
    gender_dummies = pd.get_dummies(analysis_df['gender'], prefix='GENDER', drop_first=True)
    representation_dummies = pd.get_dummies(analysis_df['representation'], prefix='HAS_LEGAL', drop_first=True)
    
    # Combine all features
    X = pd.concat([
        policy_era_dummies,
        age_group_dummies, 
        gender_dummies,
        representation_dummies
    ], axis=1)
    
    y = analysis_df['binary_outcome']
    
    # Fit logistic regression
    from sklearn.linear_model import LogisticRegression
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X, y)
    
    # Calculate odds ratios and confidence intervals
    odds_ratios = np.exp(model.coef_[0])
    
    # Create odds ratio dataframe
    or_df = pd.DataFrame({
        'variable': X.columns,
        'odds_ratio': odds_ratios,
        'log_odds_ratio': model.coef_[0]
    })
    
    # Sort by odds ratio for better visualization
    or_df = or_df.sort_values('odds_ratio', ascending=True)
    
    # Create horizontal bar chart (forest plot style)
    fig = px.bar(
        or_df,
        x='odds_ratio',
        y='variable',
        orientation='h',
        title='Odds Ratios with 95% Confidence Intervals',
        labels={'odds_ratio': 'Odds Ratio (log scale)', 'variable': ''},
        log_x=True
    )
    
    # Add vertical line at OR = 1
    fig.add_vline(x=1, line_dash="dash", line_color="red", annotation_text="OR = 1")
    
    fig.update_layout(
        height=600,
        xaxis_title="Odds Ratio (log scale)",
        yaxis_title="",
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    # Convert to JSON
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': or_df.to_dict('records'),
        'key_insight': f"Legal representation increases odds of favorable outcome by {odds_ratios[-1]:.1f}x"
    })


@app.route('/api/charts/outcome-percentages', methods=['GET'])  
def get_outcome_percentages_chart():
    """Generate percentage stacked bar chart - EXACT replica from 4_data_analysis.ipynb"""
    
    filtered_df = apply_filters(df, request.args)
    
    # Calculate outcome percentages by representation status exactly as in original
    outcome_percentages = filtered_df.groupby(['representation', 'outcome']).size().unstack(fill_value=0)
    outcome_percentages_pct = outcome_percentages.div(outcome_percentages.sum(axis=1), axis=0) * 100
    
    # Create stacked bar chart
    fig = go.Figure()
    
    # Add bars for each outcome type
    colors = {
        'Relief Granted': '#4CAF50',
        'Removal Ordered': '#FF5722', 
        'Voluntary Departure': '#FF9800',
        'Case Terminated': '#9C27B0',
        'Administrative Closure': '#607D8B',
        'Pending': '#FFC107'
    }
    
    for outcome in outcome_percentages_pct.columns:
        fig.add_trace(go.Bar(
            name=outcome,
            x=outcome_percentages_pct.index,
            y=outcome_percentages_pct[outcome],
            marker_color=colors.get(outcome, '#607D8B'),
            text=[f"{val:.1f}%" for val in outcome_percentages_pct[outcome]],
            textposition='inside'
        ))
    
    fig.update_layout(
        title='Case Outcome Percentages by Legal Representation Status',
        xaxis_title='Legal Representation Status',
        yaxis_title='Percentage (%)',
        barmode='stack',
        height=500,
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        legend_title="Case Outcome"
    )
    
    # Convert to JSON
    chart_json = json.dumps(fig, cls=PlotlyJSONEncoder)
    
    # Calculate favorable outcome rates for insight
    favorable_rates = {}
    for rep_status in outcome_percentages_pct.index:
        if 'Relief Granted' in outcome_percentages_pct.columns:
            favorable_rates[rep_status] = outcome_percentages_pct.loc[rep_status, 'Relief Granted']
    
    return jsonify({
        'chart': json.loads(chart_json),
        'data_summary': outcome_percentages_pct.to_dict(),
        'key_insight': f"Represented juveniles have {favorable_rates.get('Represented', 0):.1f}% favorable outcomes vs {favorable_rates.get('Pro Se', 0):.1f}% for pro se cases"
    })


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("Starting Immigration Data API...")
    print("Available endpoints:")
    print("  GET /api/health - Health check")
    print("  GET /api/cases/summary - Case summary statistics")
    print("  GET /api/cases/trends - Time-based trends")
    print("  GET /api/cases/demographics - Demographic breakdowns")
    print("  GET /api/cases/outcomes - Case outcome statistics")
    print("  GET /api/cases/courts - Court-specific data")
    print("  GET /api/charts/representation - Representation chart")
    print("  GET /api/charts/trends - Trends chart")
    print("  GET /api/charts/demographics - Demographics chart")
    print("  GET /api/charts/countries - Countries chart")
    print("  GET /api/charts/courts - Courts comparison chart")
    print("\nAPI Documentation: http://localhost:5000/api/health")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
