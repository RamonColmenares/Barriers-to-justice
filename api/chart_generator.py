"""
Chart generation functionality for the juvenile immigration API
"""
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.utils
from scipy import stats

try:
    from .config import START_DATE, ADMIN_CHANGES
    from .models import cache
except ImportError:
    from config import START_DATE, ADMIN_CHANGES
    from models import cache

def generate_representation_outcomes_chart():
    """Generate Plotly chart data for representation vs outcomes chart (EXACTLY like notebook)"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        # EXACTLY like notebook: Create crosstab for representation vs outcomes
        crosstab = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'], 
            analysis_filtered['BINARY_OUTCOME']
        )
        
        # EXACTLY like notebook: Calculate percentages using normalize='index' 
        # This gives percentages PER ROW (each representation category sums to 100%)
        percentage_data = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'],
            analysis_filtered['BINARY_OUTCOME'], 
            normalize='index'  # EXACTLY like notebook - normalize by rows
        ) * 100
        
        # Create Plotly figure exactly like notebook
        fig = go.Figure()
        
        # Add Favorable outcomes bar (using the percentage data from notebook logic)
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
                'type': 'log',  # Log scale exactly like in notebook
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
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return {"error": f"Chart generation error: {str(e)}"}

def generate_time_series_chart():
    """Generate Plotly time series chart exactly like notebook"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        # Filter data with valid dates from 2016 onwards (like notebook)
        date_valid = ~analysis_filtered['LATEST_HEARING'].isna()
        time_series_df = analysis_filtered[date_valid].copy()
        
        start_date = pd.Timestamp(START_DATE)
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
        shapes = []
        annotations = []
        
        for date_str, label in ADMIN_CHANGES:
            date = pd.Timestamp(date_str)
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
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return {"error": f"Chart generation error: {str(e)}"}

def generate_chi_square_analysis():
    """Generate chi-square analysis results (like notebook) - handle empty data gracefully"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {
            "message": "No analysis data available",
            "representation_by_era": {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'contingency_table': {}
            },
            "outcomes_by_representation": {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'odds_ratio': 0.0,
                'contingency_table': {},
                'percentages': {
                    'data': {},
                    'with_representation': {'favorable': 0, 'unfavorable': 0},
                    'without_representation': {'favorable': 0, 'unfavorable': 0}
                }
            }
        }
    
    results = {}
    
    # Chi-square test for representation by policy era
    try:
        era_rep_table = pd.crosstab(
            analysis_filtered['POLICY_ERA'], 
            analysis_filtered['HAS_LEGAL_REP']
        )
        
        if era_rep_table.empty or era_rep_table.values.sum() == 0:
            results['representation_by_era'] = {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'contingency_table': {}
            }
        else:
            chi2_era, p_era, dof_era, _ = stats.chi2_contingency(era_rep_table)
            n_era = era_rep_table.values.sum()
            cramer_v_era = np.sqrt(chi2_era / (n_era * (min(era_rep_table.shape) - 1))) if n_era > 0 and min(era_rep_table.shape) > 1 else 0
            
            results['representation_by_era'] = {
                'chi_square': round(float(chi2_era), 2),
                'p_value': float(p_era),
                'degrees_of_freedom': int(dof_era),
                'cramer_v': round(float(cramer_v_era), 3),
                'significant': bool(p_era < 0.05),
                'contingency_table': era_rep_table.to_dict()
            }
    except Exception as e:
        print(f"Error in era analysis: {e}")
        results['representation_by_era'] = {
            'chi_square': 0.0,
            'p_value': 1.0,
            'degrees_of_freedom': 0,
            'cramer_v': 0.0,
            'significant': False,
            'contingency_table': {}
        }
    
    # Chi-square test for outcomes by representation (EXACTLY like notebook)
    try:
        outcome_rep_table = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'],  # Put representation as index (rows)
            analysis_filtered['BINARY_OUTCOME']   # Put outcome as columns
        )
        
        if outcome_rep_table.empty or outcome_rep_table.values.sum() == 0:
            results['outcomes_by_representation'] = {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'odds_ratio': 0.0,
                'contingency_table': {},
                'percentages': {
                    'data': {},
                    'with_representation': {'favorable': 0, 'unfavorable': 0},
                    'without_representation': {'favorable': 0, 'unfavorable': 0}
                }
            }
        else:
            chi2_outcome, p_outcome, dof_outcome, _ = stats.chi2_contingency(outcome_rep_table)
            n_outcome = outcome_rep_table.values.sum()
            cramer_v_outcome = np.sqrt(chi2_outcome / (n_outcome * (min(outcome_rep_table.shape) - 1))) if n_outcome > 0 and min(outcome_rep_table.shape) > 1 else 0
            
            # Calculate percentages with normalize='index' (EXACTLY like notebook)
            percentage_data = pd.crosstab(
                analysis_filtered['HAS_LEGAL_REP'],
                analysis_filtered['BINARY_OUTCOME'], 
                normalize='index'
            ) * 100
            
            # Calculate odds ratio if we have a 2x2 table
            odds_ratio = 0.0
            if outcome_rep_table.shape == (2, 2):
                try:
                    # Using standard odds ratio calculation
                    a = outcome_rep_table.iloc[0, 0]  # Has rep, favorable
                    b = outcome_rep_table.iloc[0, 1]  # Has rep, unfavorable  
                    c = outcome_rep_table.iloc[1, 0]  # No rep, favorable
                    d = outcome_rep_table.iloc[1, 1]  # No rep, unfavorable
                    
                    if b > 0 and c > 0:  # Avoid division by zero
                        odds_ratio = (a * d) / (b * c)
                except:
                    odds_ratio = 0.0
            
            # Extract specific percentages for easy access
            rep_percentages = {}
            no_rep_percentages = {}
            
            if 'Has Legal Representation' in percentage_data.index:
                rep_row = percentage_data.loc['Has Legal Representation']
                rep_percentages = {
                    'favorable': round(rep_row.get('Favorable', 0), 1),
                    'unfavorable': round(rep_row.get('Unfavorable', 0), 1)
                }
            
            if 'No Legal Representation' in percentage_data.index:
                no_rep_row = percentage_data.loc['No Legal Representation']
                no_rep_percentages = {
                    'favorable': round(no_rep_row.get('Favorable', 0), 1),
                    'unfavorable': round(no_rep_row.get('Unfavorable', 0), 1)
                }
            
            results['outcomes_by_representation'] = {
                'chi_square': round(float(chi2_outcome), 2),
                'p_value': float(p_outcome),
                'degrees_of_freedom': int(dof_outcome),
                'cramer_v': round(float(cramer_v_outcome), 3),
                'significant': bool(p_outcome < 0.05),
                'odds_ratio': round(float(odds_ratio), 2),
                'contingency_table': outcome_rep_table.to_dict(),
                'percentages': {
                    'data': percentage_data.to_dict(),
                    'with_representation': rep_percentages,
                    'without_representation': no_rep_percentages
                }
            }
            
    except Exception as e:
        print(f"Error in outcome analysis: {e}")
        results['outcomes_by_representation'] = {
            'chi_square': 0.0,
            'p_value': 1.0,
            'degrees_of_freedom': 0,
            'cramer_v': 0.0,
            'significant': False,
            'odds_ratio': 0.0,
            'contingency_table': {},
            'percentages': {
                'data': {},
                'with_representation': {'favorable': 0, 'unfavorable': 0},
                'without_representation': {'favorable': 0, 'unfavorable': 0}
            }
        }
    
    return results

def generate_outcome_percentages_chart():
    """Generate the percentage breakdown chart EXACTLY like notebook"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        # Calculate percentages exactly like notebook
        percentage_data = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'],
            analysis_filtered['BINARY_OUTCOME'], 
            normalize='index'
        ) * 100
        
        # Create Plotly figure
        fig = go.Figure()
        
        # Add bars for each outcome
        for outcome in percentage_data.columns:
            color = '#10B981' if outcome == 'Favorable' else '#EF4444'
            fig.add_trace(go.Bar(
                name=outcome,
                x=percentage_data.index,
                y=percentage_data[outcome],
                marker_color=color,
                text=[f"{p:.1f}%" for p in percentage_data[outcome]],
                textposition='inside',
                textfont=dict(color='white', size=12)
            ))
        
        # Update layout
        fig.update_layout(
            title={
                'text': 'Case Outcome Percentages by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif'}
            },
            barmode='stack',
            xaxis={
                'title': 'Legal Representation',
                'title_font': {'size': 14}
            },
            yaxis={
                'title': 'Percentage',
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
        return json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        
    except Exception as e:
        return {"error": f"Chart generation error: {str(e)}"}
