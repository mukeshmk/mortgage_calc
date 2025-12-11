import streamlit as st
import pandas as pd
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mortgage_lib.models import ScenarioConfig, LoanDetails, AnalysisSettings, RateChange, Overpayment
from mortgage_lib.scenarios import expand_scenarios
from mortgage_lib.calculation import calculate_mortgage

st.set_page_config(page_title="Mortgage Calculator", layout="wide")

st.title("Mortgage Calculator & Comparison")

with st.sidebar:
    st.header("Loan Details")
    principal = st.number_input("Principal Amount", value=425000, step=1000)
    start_rate = st.number_input("Initial Interest Rate (%)", value=4.3, step=0.1)
    years = st.number_input("Loan Term (Years)", value=30)
    
    st.header("Analysis Options")
    window_start = st.number_input("Analysis Window Start (Month)", value=13)
    window_end = st.number_input("Analysis Window End (Month)", value=61)

    st.header("Rate Changes")
    # Simple UI for adding rate changes is tricky, let's just do a text input for JSON or a fixed number of slots?
    # Better: Use st.data_editor or just a few fixed inputs for now to keep it simple, 
    # or handle the JSON structure from the original config file.
    # Let's support loading from config first, that's easier.
    
    uploaded_file = st.file_uploader("Upload Config JSON (Optional)", type="json")
    
    overpayment_amount = st.number_input("Overpayment (Generic)", value=0)
    overpayment_month = st.number_input("Month for Overpayment", value=1)


# Construct config object
import json

if uploaded_file is not None:
    config_data = json.load(uploaded_file)
    # Validate/Convert to Pydantic if needed or manual map
    # Ideally should map perfectly if structure matches
    try:
        config = ScenarioConfig(**config_data)
        st.success("Configuration loaded from file!")
    except Exception as e:
        st.error(f"Error loading config: {e}")
        config = None
else:
    # Build from UI Inputs
    # This is a basic construction
    base_loan = LoanDetails(principal=principal, start_rate=start_rate, years=years)
    analysis_settings = AnalysisSettings(window_start_month=window_start, window_end_month=window_end)
    
    # Simple rate change adder?
    # For now let's just use the overpayment input as a single overpayment event
    overpayments = []
    if overpayment_amount > 0:
        overpayments.append(Overpayment(month=overpayment_month, amount=overpayment_amount))
        
    config = ScenarioConfig(
        base_loan=base_loan,
        analysis_settings=analysis_settings,
        rate_changes=[], # UI for this is complex, leaving empty for basic manual mode
        overpayments=overpayments
    )

if st.button("Calculate"):
    if config:
        scenarios = expand_scenarios(config)
        results = []
        for s in scenarios:
            results.append(calculate_mortgage(s, return_schedule=True))
            
        # Display Results
        
        # Summary Table
        summary_data = []
        for r in results:
            summary_data.append({
                "Scenario": r['name'],
                "Window Interest": r['window_interest'],
                "Lifetime Interest": r['lifetime_interest'],
                "Balance @ End Window": r['balance_at_window_end']
            })
        
        st.subheader("Summary")
        st.dataframe(pd.DataFrame(summary_data))
        
        # Charts
        st.subheader("Balance Over Time")
        all_dfs = []
        for r in results:
            if 'schedule' in r:
                df = pd.DataFrame(r['schedule'])
                df['Scenario'] = r['name']
                all_dfs.append(df)
        
        if all_dfs:
            combined_df = pd.concat(all_dfs)
            st.line_chart(combined_df, x='Month', y='End Balance', color='Scenario')
            
            st.subheader("Interest Paid Over Time")
            st.line_chart(combined_df, x='Month', y='Cumulative Interest', color='Scenario')
            
            # Show Raw Data for first scenario or selected
            st.subheader("Detailed Schedule")
            selected_scenario = st.selectbox("Select Scenario", [r['name'] for r in results])
            if selected_scenario:
                scenario_res = next(r for r in results if r['name'] == selected_scenario)
                st.dataframe(pd.DataFrame(scenario_res['schedule']))

