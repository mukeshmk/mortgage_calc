import csv
import json
import math
import os
import copy
import pandas as pd

def calculate_monthly_payment(principal, annual_rate, years):
    """
    Calculates the monthly payment for a loan.
    Formula: M = P [ i(1 + i)^n ] / [ (1 + i)^n – 1 ]
    """
    if annual_rate == 0:
        return principal / (years * 12)
    
    monthly_rate = annual_rate / 100 / 12
    num_payments = years * 12
    
    if num_payments <= 0:
        return principal
        
    payment = principal * (monthly_rate * math.pow(1 + monthly_rate, num_payments)) / (math.pow(1 + monthly_rate, num_payments) - 1)
    return payment

def load_config(filepath):
    """Loads the mortgage configuration from a JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def expand_scenarios(json_data):
    """
    Parses the configuration and branches scenarios whenever a rate change
    has a list of options.
    Returns a list of complete scenario objects.
    """
    base_scenario = {
        "name": "Base Scenario",
        "loan_details": json_data['base_loan'],
        "rate_changes": [],
        "overpayments": json_data.get('overpayments', []),
        "analysis_settings": json_data.get('analysis_settings', {})
    }

    raw_rate_changes = json_data.get('rate_changes', [])
    
    def build_branches(current_scenario_config, remaining_changes):
        if not remaining_changes:
            return [current_scenario_config]
        
        next_change = remaining_changes[0]
        rest_changes = remaining_changes[1:]
        
        branches = []
        
        if isinstance(next_change['new_rate'], list):
            print(f"  [Branching] Found list of rates for Month {next_change['month']}: {next_change['new_rate']}")
            for rate_option in next_change['new_rate']:
                new_branch = copy.deepcopy(current_scenario_config)
                single_event = copy.deepcopy(next_change)
                single_event['new_rate'] = rate_option
                new_branch['rate_changes'].append(single_event)
                new_branch['name'] += f" -> Rate {rate_option}% @ M{next_change['month']}"
                branches.extend(build_branches(new_branch, rest_changes))
        else:
            current_scenario_config['rate_changes'].append(next_change)
            branches.extend(build_branches(current_scenario_config, rest_changes))
            
        return branches

    print(f"[{'Scenario Expansion':^20}] Starting...")
    base_scenario['name'] = "Scenario" 
    expanded_scenarios = build_branches(base_scenario, raw_rate_changes)
    print(f"[{'Scenario Expansion':^20}] Finished. Total Scenarios: {len(expanded_scenarios)}")
    return expanded_scenarios

def calculate_mortgage(scenario_data, return_schedule=False, verbose=False):
    """
    Simulates the mortgage.
    If return_schedule is True, includes the full monthly data list in the return dict.
    """
    loan_details = scenario_data['loan_details']
    original_principal = loan_details['principal']
    current_balance = original_principal
    current_rate = loan_details['start_rate']
    total_years = loan_details['years']
    
    analysis_window = scenario_data.get('analysis_settings', {})
    window_start = analysis_window.get('window_start_month', 1)
    window_end = analysis_window.get('window_end_month', 12)
    
    rate_changes = {item['month']: item['new_rate'] for item in scenario_data.get('rate_changes', [])}
    overpayments = {item['month']: item['amount'] for item in scenario_data.get('overpayments', [])}
    
    total_months_originally_planned = total_years * 12
    
    monthly_payment = calculate_monthly_payment(current_balance, current_rate, total_years)

    total_interest_paid = 0
    total_principal_paid = 0
    
    window_interest = 0
    window_principal = 0
    balance_at_window_end = 0
    
    month = 1
    schedule_data = []
    
    cumulative_interest = 0
    cumulative_principal = 0
    cumulative_total_paid = 0
    
    if verbose:
        print(f"\n--- Simulating: {scenario_data['name']} ---")
        print(f"Start Rate: {current_rate}%, Window: M{window_start}-{window_end}")

    while current_balance > 0.01:
        start_balance = current_balance
        overpayment_amount = 0
        
        if month in rate_changes:
            new_rate = rate_changes[month]
            if verbose: print(f"  [Event] Month {month}: Rate change {current_rate}% -> {new_rate}%")
            current_rate = new_rate
            remaining_term_months = total_months_originally_planned - (month - 1)
            monthly_payment = calculate_monthly_payment(current_balance, current_rate, remaining_term_months / 12)

        monthly_interest_rate = current_rate / 100 / 12
        interest_payment = current_balance * monthly_interest_rate
        total_interest_paid += interest_payment
        
        if month in overpayments:
            overpayment_amount = overpayments[month]
            if verbose: print(f"  [Event] Month {month}: Overpayment of ${overpayment_amount}")
            current_balance -= overpayment_amount
            total_principal_paid += overpayment_amount
            
            if current_balance <= 0:
                if verbose: print(f"  [Info] Loan paid off via overpayment at Month {month}")

        amount_to_pay = monthly_payment
        principal_component = 0
        
        if current_balance > 0:
             principal_component = amount_to_pay - interest_payment
             
             if current_balance < principal_component:
                  amount_to_pay = current_balance + interest_payment
                  principal_component = current_balance
             
             current_balance -= principal_component
             total_principal_paid += principal_component
        
        # Capture data for schedule
        if return_schedule:
            cumulative_interest += interest_payment
            cumulative_principal += (principal_component + overpayment_amount)
            cumulative_total_paid += amount_to_pay + overpayment_amount if month in overpayments else amount_to_pay 
            
            schedule_data.append({
                "Month": month,
                "Rate (%)": current_rate,
                "Start Balance": round(start_balance, 2),
                "Monthly Payment": round(amount_to_pay, 2),
                "Interest Paid": round(interest_payment, 2),
                "Principal Paid": round(principal_component + overpayment_amount, 2), # Combine regular + overpayment
                "Overpayment": round(overpayment_amount, 2),
                "End Balance": round(max(0, current_balance), 2),
                "Cumulative Interest": round(cumulative_interest, 2),
                "Cumulative Principal": round(cumulative_principal, 2),
                "Total Paid To Date": round(cumulative_total_paid, 2)
            })

        if window_start <= month <= window_end:
            window_interest += interest_payment
            window_principal += (principal_component + overpayment_amount)
            if month == window_end:
                balance_at_window_end = current_balance

        if current_balance <= 0.001: 
             if month < window_end and balance_at_window_end == 0:
                 balance_at_window_end = 0
             break
             
        month += 1
        
        if month > total_months_originally_planned * 2: 
            break
            
    if month <= window_end:
        balance_at_window_end = 0

    result = {
        "name": scenario_data['name'],
        "window_interest": window_interest,
        "window_principal": window_principal,
        "balance_at_window_end": balance_at_window_end,
        "lifetime_interest": total_interest_paid
    }
    
    if return_schedule:
        result["schedule"] = schedule_data
        
    return result

def export_reports(results, output_dir):
    """
    Generates CSV for cheapest scenario and Excel for comparison.
    """
    sorted_by_total_int = sorted(results, key=lambda x: x['lifetime_interest'])
    cheapest = sorted_by_total_int[0]
    
    print(f"\n[{'Reporting':^20}] Cheapest Scenario Identified: {cheapest['name']}")
    
    if 'schedule' not in cheapest:
         pass
         
    df_cheapest = pd.DataFrame(cheapest['schedule'])
    csv_path = os.path.join(output_dir, "mortgage_schedule.csv")
    df_cheapest.to_csv(csv_path, index=False)
    print(f"[{'CSV Export':^20}] Saved to {csv_path}")

    # Excel Comparison
    all_schedules = {r['name']: pd.DataFrame(r['schedule']) for r in results}
    
    merged = None
    for name, df in all_schedules.items():
        temp = df[['Month', 'Rate (%)']].copy()
        temp.columns = ['Month', f'Rate_{name}']
        if merged is None:
            merged = temp
        else:
            merged = pd.merge(merged, temp, on='Month', how='outer')
            
    rate_cols = [c for c in merged.columns if c.startswith('Rate_')]
    merged['diff'] = merged[rate_cols].max(axis=1) != merged[rate_cols].min(axis=1)
    diff_months = merged[merged['diff']]['Month'].tolist()
    
    excel_path = os.path.join(output_dir, "scenario_comparison.xlsx")
    
    if not diff_months:
        print(f"[{'Excel Export':^20}] No rate differences found. Skipping.")
    else:
        min_month = min(diff_months)
        max_month = max(diff_months)
        print(f"[{'Excel Export':^20}] Differing Period: Month {min_month} to {max_month}. Exporting...")
        
        with pd.ExcelWriter(excel_path) as writer:
            for name, df in all_schedules.items():
                mask = (df['Month'] >= min_month) & (df['Month'] <= max_month)
                filtered_df = df[mask]
                
                sheet_name = name.replace("Scenario -> ", "").replace("Rate ", "").replace("%", "")[:30]
                for ch in ['[', ']', ':', '*', '?', '/', '\\']:
                    sheet_name = sheet_name.replace(ch, '')
                
                filtered_df.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"[{'Excel Export':^20}] Saved to {excel_path}")

def run_comparison_engine(config_path):
    print(f"\n{'='*60}")
    print(f"{'MORTGAGE COMPARISON ENGINE':^60}")
    print(f"{'='*60}\n")
    print(f"Loading configuration from {config_path}...")
    try:
        config_data = load_config(config_path)
    except FileNotFoundError:
        print("Error: Config file not found.")
        return

    scenarios = expand_scenarios(config_data)
    
    results = []
    print(f"\n[{'Calculation':^20}] Processing {len(scenarios)} scenarios...")
    for i, sc in enumerate(scenarios, 1):
        print(f"  -> Simulating Scenario {i}/{len(scenarios)}: {sc['name']}")
        res = calculate_mortgage(sc, return_schedule=True, verbose=False)
        results.append(res)
        
    min_window_interest = min(r['window_interest'] for r in results)
    
    print(f"\n{'='*105}")
    print(f"{'COMPARISON RESULTS':^105}")
    print(f"{'='*105}")
    print(f"{'Scenario Name':<45} | {'Window Int':<12} | {'Window Prin':<12} | {'Bal @ M24':<12} | {'Lifetime Int':<12}")
    print("-" * 105)
    
    for r in results:
        name = r['name']
        w_int = r['window_interest']
        w_prin = r['window_principal']
        bal = r['balance_at_window_end']
        l_int = r['lifetime_interest']
        
        is_cheaper = (abs(w_int - min_window_interest) < 0.01)
        cheaper_mark = "(CHEAPER)" if is_cheaper else ""
        
        display_name = (name[:42] + '..') if len(name) > 42 else name
        print(f"{display_name:<45} | ${w_int:<11,.2f} | ${w_prin:<11,.2f} | ${bal:<11,.2f} | ${l_int:<11,.2f} {cheaper_mark}")
    
    print("-" * 105)
    export_reports(results, os.path.dirname(config_path))
    print(f"\n{'='*60}")
    print(f"{'DONE':^60}")
    print(f"{'='*60}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'mortgage_config.json')
    run_comparison_engine(config_path)
