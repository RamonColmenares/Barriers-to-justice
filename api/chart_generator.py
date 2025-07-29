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
    """Generate Plotly chart for representation vs outcomes (EXACTLY like notebook)"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        print("Generating representation outcomes chart EXACTLY like notebook...")
        
        # EXACTLY like notebook: Create count data
        crosstab_counts = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'], 
            analysis_filtered['BINARY_OUTCOME']
        )
        
        print("Count data:")
        print(crosstab_counts)
        
        # EXACTLY like notebook: Calculate percentages (normalize by index - each row sums to 100%)
        percentage_data = pd.crosstab(
            analysis_filtered['HAS_LEGAL_REP'],
            analysis_filtered['BINARY_OUTCOME'], 
            normalize='index'  # EXACTLY like notebook - percentages within each representation category
        ) * 100
        
        print("Percentage data:")
        print(percentage_data.round(1))
        
        # Create Plotly figure for count plot with log scale (EXACTLY like notebook)
        fig = go.Figure()
        
        # Custom colors EXACTLY like notebook
        colors = {
            'Favorable': '#B5E68160',  # Light green with transparency
            'Unfavorable': '#FF5E5E7D'  # Light red with transparency  
        }
        
        # Get the categories (representation levels)
        categories = crosstab_counts.index.tolist()
        
        # Add bars for each outcome type
        for outcome in ['Favorable', 'Unfavorable']:
            if outcome in crosstab_counts.columns:
                # Get percentages for text labels
                percentages = percentage_data[outcome] if outcome in percentage_data.columns else [0] * len(categories)
                
                fig.add_trace(go.Bar(
                    name=outcome,
                    x=categories,
                    y=crosstab_counts[outcome],
                    marker_color=colors.get(outcome, '#888888'),
                    text=[f"{p:.1f}%" for p in percentages],
                    textposition='inside',
                    textfont=dict(color='white', size=12, weight='bold')
                ))
        
        # Update layout EXACTLY like notebook
        fig.update_layout(
            title={
                'text': 'Case Outcomes by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif', 'color': '#333'}
            },
            barmode='group',  # Side by side bars like seaborn countplot
            xaxis={
                'title': 'Legal Representation',
                'tickangle': 0,
                'title_font': {'size': 14},
                'showgrid': False
            },
            yaxis={
                'title': 'Count',
                'type': 'log',  # Log scale EXACTLY like notebook
                'title_font': {'size': 14},
                'showgrid': True,
                'gridcolor': 'rgba(128,128,128,0.3)'
            },
            showlegend=True,
            legend=dict(
                title='Case Outcome',
                orientation='v',
                x=1.02,
                y=1
            ),
            margin=dict(t=80, l=80, r=120, b=100),
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
        
        # Also return summary data for debugging
        summary_data = {
            'count_data': crosstab_counts.to_dict(),
            'percentage_data': percentage_data.round(1).to_dict(),
            'total_cases': len(analysis_filtered)
        }
        
        # Convert to JSON-serializable format
        result = json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        result['summary'] = summary_data
        
        return result
        
    except Exception as e:
        print(f"Chart generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Chart generation error: {str(e)}"}

def generate_outcome_percentages_chart():
    """Generate the percentage breakdown chart EXACTLY like notebook (stacked bar chart)"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        print("Generating outcome percentages chart EXACTLY like notebook...")
        
        # EXACTLY like notebook: Calculate percentages correctly
        percentage_data = (
            pd.crosstab(
                analysis_filtered["HAS_LEGAL_REP"],
                analysis_filtered["BINARY_OUTCOME"],
                normalize="index",  # EXACTLY like notebook - normalize by rows
            )
            * 100
        )
        
        print("Percentage breakdown of outcomes by legal representation:")
        print(percentage_data.round(1))
        
        # Create stacked bar chart EXACTLY like notebook
        fig = go.Figure()
        
        # Colors for the stacked chart (using Set2 colormap style)
        colors = {
            'Favorable': '#66C2A5',  # Green
            'Unfavorable': '#FC8D62'  # Orange/Red
        }
        
        categories = percentage_data.index.tolist()
        
        # Add stacked bars for each outcome
        for outcome in ['Favorable', 'Unfavorable']:
            if outcome in percentage_data.columns:
                fig.add_trace(go.Bar(
                    name=outcome,
                    x=categories,
                    y=percentage_data[outcome],
                    marker_color=colors.get(outcome, '#888888'),
                    text=[f"{p:.1f}%" for p in percentage_data[outcome]],
                    textposition='inside',
                    textfont=dict(color='white', size=12, weight='bold')
                ))
        
        # Update layout EXACTLY like notebook
        fig.update_layout(
            title={
                'text': 'Case Outcome Percentages by Legal Representation Status',
                'x': 0.5,
                'font': {'size': 16, 'family': 'Arial, sans-serif', 'color': '#333'}
            },
            barmode='stack',  # Stacked bars EXACTLY like notebook
            xaxis={
                'title': 'Legal Representation',
                'tickangle': 0,
                'title_font': {'size': 14},
                'showgrid': False
            },
            yaxis={
                'title': 'Percentage (%)',
                'title_font': {'size': 14},
                'showgrid': True,
                'gridcolor': 'rgba(128,128,128,0.3)',
                'range': [0, 100]
            },
            showlegend=True,
            legend=dict(
                title='Case Outcome',
                orientation='v',
                x=1.02,
                y=1
            ),
            margin=dict(t=80, l=80, r=120, b=100),
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
        
        # Also return the actual percentage values
        summary_data = {
            'percentage_breakdown': percentage_data.round(1).to_dict(),
            'total_cases': len(analysis_filtered)
        }
        
        # Convert to JSON-serializable format
        result = json.loads(plotly.utils.PlotlyJSONEncoder().encode(chart_data))
        result['summary'] = summary_data
        
        return result
        
    except Exception as e:
        print(f"Percentage chart generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": f"Percentage chart generation error: {str(e)}"}

def generate_time_series_chart():
    """Generate Plotly time series chart with focused timeframe exactly like notebook"""
    analysis_filtered = cache.get('analysis_filtered')
    
    if analysis_filtered is None or analysis_filtered.empty:
        return {"error": "No analysis data available"}
    
    try:
        # Filter data with valid dates (like notebook)
        date_valid = ~analysis_filtered['LATEST_HEARING'].isna()
        time_series_df = analysis_filtered[date_valid].copy()
        
        # Create quarterly data (like notebook)
        time_series_df['YEAR_QUARTER'] = time_series_df['LATEST_HEARING'].dt.to_period('Q')
        
        quarterly_rep = time_series_df.groupby('YEAR_QUARTER').agg(
            total_cases=('HAS_LEGAL_REP', 'count'),
            represented_cases=('HAS_LEGAL_REP', lambda x: (x == 'Has Legal Representation').sum())
        )
        quarterly_rep['representation_rate'] = quarterly_rep['represented_cases'] / quarterly_rep['total_cases']
        
        # Plot representation rates over time with focused timeframe
        quarterly_rep["YEAR_QUARTER_START"] = quarterly_rep.index.to_timestamp()
        
        # Filter to only show data from 2016 to present (with small buffer)
        # This focuses on the relevant administrations for your research question
        start_date = pd.Timestamp("2016-01-01")  # Just before Trump's first term
        end_date = pd.Timestamp("2025-12-31")  # Just after start of Trump's second term
        current_date = pd.Timestamp.now()
        
        # Filter the data to the relevant timeframe
        filtered_data = quarterly_rep[
            (quarterly_rep["YEAR_QUARTER_START"] >= start_date)
            & (quarterly_rep["YEAR_QUARTER_START"] <= current_date)
        ]
        
        # Create Plotly figure exactly like notebook
        fig = go.Figure()
        
        # Plot the main time series line with filtered data
        fig.add_trace(go.Scatter(
            x=filtered_data["YEAR_QUARTER_START"],
            y=filtered_data["representation_rate"],
            mode='lines+markers',
            name='Representation Rate',
            line=dict(color='navy', width=2),
            marker=dict(size=6, color='navy'),
            opacity=0.7
        ))
        
        # Add administration changes as vertical lines
        admin_changes = [
            (pd.Timestamp("2017-01-20"), "Trump Administration"),
            (pd.Timestamp("2021-01-20"), "Biden Administration"),
            (pd.Timestamp("2025-01-20"), "Trump Administration II"),
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
                y=0.05,  # Position at bottom like in your code
                text=label,
                showarrow=False,
                textangle=-90,
                xanchor="right",
                yanchor="bottom",
                font=dict(size=10, color="red")
            ))
        
        # Update layout to match notebook exactly
        fig.update_layout(
            title={
                'text': 'Legal Representation Rate for Juvenile Immigration Cases (2016-2025)',
                'x': 0.5,
                'font': {'size': 14, 'family': 'Arial, sans-serif'}
            },
            xaxis={
                'title': 'Year',
                'title_font': {'size': 14},
                'tickformat': '%Y'  # Format x-axis to show years clearly
            },
            yaxis={
                'title': 'Representation Rate',
                'title_font': {'size': 14},
                'range': [0, 1]  # Adjust as needed based on your data
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
        
        # Add grid with alpha transparency like in notebook
        fig.update_yaxes(showgrid=True, gridcolor='rgba(128,128,128,0.3)')
        fig.update_xaxes(showgrid=True, gridcolor='rgba(128,128,128,0.3)')
        
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
                'contingency_table': {},
                'interpretation': "No data available for analysis"
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
                },
                'interpretation': "No data available for analysis",
                'odds_interpretation': "No data available for analysis"
            }
        }
    
    results = {}
    
    # Chi-square test for representation by policy era
    try:
        # Create a contingency table for legal representation by policy era
        era_rep_table = pd.crosstab(
            analysis_filtered["POLICY_ERA"], 
            analysis_filtered["HAS_LEGAL_REP"]
        )
        print("Contingency Table: Legal Representation by Policy Era")
        print(era_rep_table)
        
        if era_rep_table.empty or era_rep_table.values.sum() == 0:
            results['representation_by_era'] = {
                'chi_square': 0.0,
                'p_value': 1.0,
                'degrees_of_freedom': 0,
                'cramer_v': 0.0,
                'significant': False,
                'contingency_table': {},
                'interpretation': "No data available for analysis"
            }
        else:
            # Perform chi-square test for legal representation by policy era
            chi2_era_rep, p_era_rep, dof_era_rep, expected_era_rep = stats.chi2_contingency(era_rep_table)
            
            # Calculate Cramer's V for effect size
            n = era_rep_table.values.sum()
            cramer_v = np.sqrt(chi2_era_rep / (n * (min(era_rep_table.shape) - 1))) if n > 0 and min(era_rep_table.shape) > 1 else 0
            
            print("Chi-Square Test Results: Legal Representation by Policy Era")
            print(f"Chi-square statistic: {chi2_era_rep:.2f}")
            print(f"p-value: {p_era_rep}")
            print(f"Degrees of freedom: {dof_era_rep}")
            
            # Generate interpretation
            interpretation = "Interpretation:\n"
            if p_era_rep < 0.05:
                interpretation += "The relationship between policy era and legal representation is statistically significant (p < 0.05). "
                interpretation += "The null hypothesis that there is no association between these variables can be rejected."
            else:
                interpretation += "No statistically significant relationship was found between policy era and legal representation."
            interpretation += f"\n\nCramer's V (effect size): {cramer_v:.3f}\nThis indicates a small effect size."
            
            print(interpretation)
            
            results['representation_by_era'] = {
                'chi_square': round(float(chi2_era_rep), 2),
                'p_value': float(p_era_rep),
                'degrees_of_freedom': int(dof_era_rep),
                'cramer_v': round(float(cramer_v), 3),
                'significant': bool(p_era_rep < 0.05),
                'contingency_table': era_rep_table.to_dict(),
                'interpretation': interpretation
            }
    except Exception as e:
        print(f"Error in era analysis: {e}")
        results['representation_by_era'] = {
            'chi_square': 0.0,
            'p_value': 1.0,
            'degrees_of_freedom': 0,
            'cramer_v': 0.0,
            'significant': False,
            'contingency_table': {},
            'interpretation': f"Error in analysis: {str(e)}"
        }
    
    # Chi-square test for outcomes by representation (EXACTLY like notebook)
    try:
        # Create a contingency table for case outcomes by legal representation
        outcome_rep_table = pd.crosstab(
            analysis_filtered["BINARY_OUTCOME"], 
            analysis_filtered["HAS_LEGAL_REP"]
        )
        print("Contingency Table: Case Outcomes by Legal Representation")
        print(outcome_rep_table)
        
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
                },
                'interpretation': "No data available for analysis",
                'odds_interpretation': "No data available for analysis"
            }
        else:
            # Perform chi-square test for case outcomes by legal representation
            chi2_outcome_rep, p_outcome_rep, dof_outcome_rep, expected_outcome_rep = stats.chi2_contingency(outcome_rep_table)
            
            # Calculate Cramer's V for effect size
            n = outcome_rep_table.values.sum()
            cramer_v = np.sqrt(chi2_outcome_rep / (n * (min(outcome_rep_table.shape) - 1))) if n > 0 and min(outcome_rep_table.shape) > 1 else 0
            
            print("Chi-Square Test Results: Case Outcomes by Legal Representation")
            print(f"Chi-square statistic: {chi2_outcome_rep:.2f}")
            print(f"p-value: {p_outcome_rep}")
            print(f"Degrees of freedom: {dof_outcome_rep}")
            
            # Generate interpretation
            interpretation = "Interpretation:\n"
            if p_outcome_rep < 0.05:
                interpretation += "The relationship between legal representation and case outcomes is statistically significant (p < 0.05). "
                interpretation += "The null hypothesis that there is no association between these variables can be rejected."
            else:
                interpretation += "No statistically significant relationship was found between legal representation and case outcomes."
            interpretation += f"\n\nCramer's V (effect size): {cramer_v:.3f}\nThis indicates a moderate to strong effect size."
            
            print(interpretation)
            
            # Calculate percentages with normalize='index' for comparison table
            percentage_data_for_table = pd.crosstab(
                analysis_filtered['HAS_LEGAL_REP'],
                analysis_filtered['BINARY_OUTCOME'], 
                normalize='index'
            ) * 100
            
            # Calculate odds ratio if we have the right structure
            odds_ratio = 0.0
            odds_with_rep = 0.0
            odds_without_rep = 0.0
            odds_interpretation = ""
            
            try:
                # Calculate odds ratio for favorable outcomes by representation
                a = outcome_rep_table.loc["Favorable", "Has Legal Representation"]
                b = outcome_rep_table.loc["Unfavorable", "Has Legal Representation"] 
                c = outcome_rep_table.loc["Favorable", "No Legal Representation"]
                d = outcome_rep_table.loc["Unfavorable", "No Legal Representation"]

                odds_with_rep = a / b if b > 0 else 0
                odds_without_rep = c / d if d > 0 else 0
                odds_ratio = odds_with_rep / odds_without_rep if odds_without_rep > 0 else 0

                print("\nOdds Ratio Calculation:")
                print(f"Odds of favorable outcome with representation: {odds_with_rep:.3f}")
                print(f"Odds of favorable outcome without representation: {odds_without_rep:.3f}")
                print(f"Odds ratio: {odds_ratio:.3f}")
                
                odds_interpretation = f"Interpretation: Juveniles with legal representation are {odds_ratio:.2f} times more likely to receive a favorable outcome compared to those without representation."
                print(f"\n{odds_interpretation}")
                
            except Exception as odds_error:
                print(f"Could not calculate odds ratio: {odds_error}")
                odds_interpretation = "Could not calculate odds ratio due to data structure"
            
            # Extract specific percentages for easy access
            rep_percentages = {}
            no_rep_percentages = {}
            
            if 'Has Legal Representation' in percentage_data_for_table.index:
                rep_row = percentage_data_for_table.loc['Has Legal Representation']
                rep_percentages = {
                    'favorable': round(rep_row.get('Favorable', 0), 1),
                    'unfavorable': round(rep_row.get('Unfavorable', 0), 1)
                }
            
            if 'No Legal Representation' in percentage_data_for_table.index:
                no_rep_row = percentage_data_for_table.loc['No Legal Representation']
                no_rep_percentages = {
                    'favorable': round(no_rep_row.get('Favorable', 0), 1),
                    'unfavorable': round(no_rep_row.get('Unfavorable', 0), 1)
                }
            
            results['outcomes_by_representation'] = {
                'chi_square': round(float(chi2_outcome_rep), 2),
                'p_value': float(p_outcome_rep),
                'degrees_of_freedom': int(dof_outcome_rep),
                'cramer_v': round(float(cramer_v), 3),
                'significant': bool(p_outcome_rep < 0.05),
                'odds_ratio': round(float(odds_ratio), 3),
                'odds_with_representation': round(float(odds_with_rep), 3),
                'odds_without_representation': round(float(odds_without_rep), 3),
                'contingency_table': outcome_rep_table.to_dict(),
                'percentages': {
                    'data': percentage_data_for_table.to_dict(),
                    'with_representation': rep_percentages,
                    'without_representation': no_rep_percentages
                },
                'interpretation': interpretation,
                'odds_interpretation': odds_interpretation
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
            },
            'interpretation': f"Error in analysis: {str(e)}",
            'odds_interpretation': f"Error in analysis: {str(e)}"
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
