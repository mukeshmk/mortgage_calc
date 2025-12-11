import csv
import json
import math
import os
import copy

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

    # We need to process rate_changes. If any change has a list for 'new_rate',
    # we branch.
    raw_rate_changes = json_data.get('rate_changes', [])
    
    # Recursive function to build scenarios
    def build_branches(current_scenario_config, remaining_changes):
        if not remaining_changes:
            return [current_scenario_config]
        
        next_change = remaining_changes[0]
        rest_changes = remaining_changes[1:]
        
        branches = []
        
        # Check if new_rate is a list
        if isinstance(next_change['new_rate'], list):
            for rate_option in next_change['new_rate']:
                # Create a new branch
                new_branch = copy.deepcopy(current_scenario_config)
                
                # Update the specific event to have a single float rate
                single_event = copy.deepcopy(next_change)
                single_event['new_rate'] = rate_option
                new_branch['rate_changes'].append(single_event)
                
                # Append to name to track the path
                new_branch['name'] += f" -> Rate {rate_option}% @ M{next_change['month']}"
                
                # Recurse
                branches.extend(build_branches(new_branch, rest_changes))
        else:
            # No branching, just add and move on
            current_scenario_config['rate_changes'].append(next_change)
            branches.extend(build_branches(current_scenario_config, rest_changes))
            
        return branches

    # Start recursion
    # We clean the name of the base first so it doesn't get too long if we want
    base_scenario['name'] = "Scenario" 
    expanded_scenarios = build_branches(base_scenario, raw_rate_changes)
    
    # Clean up names for the final output as per requirement
    # "Scenario - Rate Option 3.3%" etc.
    # The simple recursion appended strings. Let's do a pass to make them pretty if needed.
    # For now, the recursive name building "Scenario -> Rate 3.3% @ M13" is quite descriptive.
    
    return expanded_scenarios

def calculate_mortgage(scenario_data):
    """
    Simulates the mortgage month-by-month based on configuration.
    Returns a dictionary of metrics including window analysis.
    """
    loan_details = scenario_data['loan_details']
    original_principal = loan_details['principal']
    current_balance = original_principal
    current_rate = loan_details['start_rate']
    total_years = loan_details['years']
    
    analysis_window = scenario_data.get('analysis_settings', {})
    window_start = analysis_window.get('window_start_month', 1)
    window_end = analysis_window.get('window_end_month', 12)
    
    # Pre-process events for easier lookup
    rate_changes = {item['month']: item['new_rate'] for item in scenario_data.get('rate_changes', [])}
    overpayments = {item['month']: item['amount'] for item in scenario_data.get('overpayments', [])}
    
    total_months_originally_planned = total_years * 12
    
    monthly_payment = calculate_monthly_payment(current_balance, current_rate, total_years)

    total_interest_paid = 0
    total_principal_paid = 0
    
    # Window metrics
    window_interest = 0
    window_principal = 0
    balance_at_window_end = 0
    
    month = 1
    
    while current_balance > 0.01:
        start_balance = current_balance
        overpayment_amount = 0
        
        # 1. Check for Rate Change
        if month in rate_changes:
            new_rate = rate_changes[month]
            current_rate = new_rate
            
            remaining_term_months = total_months_originally_planned - (month - 1)
            monthly_payment = calculate_monthly_payment(current_balance, current_rate, remaining_term_months / 12)

        # 2. Calculate Interest
        monthly_interest_rate = current_rate / 100 / 12
        interest_payment = current_balance * monthly_interest_rate
        total_interest_paid += interest_payment
        
        # 3. Check for Overpayments
        if month in overpayments:
            overpayment_amount = overpayments[month]
            current_balance -= overpayment_amount
            # Note: Overpayment is principal paid
            total_principal_paid += overpayment_amount
            
            if current_balance <= 0:
                pass

        # 4. Process Regular Payment
        amount_to_pay = monthly_payment
        principal_component = 0
        
        if current_balance > 0:
             principal_component = amount_to_pay - interest_payment
             
             if current_balance < principal_component:
                  amount_to_pay = current_balance + interest_payment
                  principal_component = current_balance
             
             current_balance -= principal_component
             total_principal_paid += principal_component
        
        # Window Logic
        if window_start <= month <= window_end:
            window_interest += interest_payment
            window_principal += (principal_component + overpayment_amount)
            if month == window_end:
                balance_at_window_end = current_balance

        if current_balance <= 0.001: 
             # If we paid off before window end, balance is 0
             if month < window_end and balance_at_window_end == 0:
                 balance_at_window_end = 0
             break
             
        month += 1
        
        if month > total_months_originally_planned * 2: 
            break
            
    # If the simulation ended before the window end (paid off), ensure balance is recorded as 0
    if month <= window_end:
        balance_at_window_end = 0

    return {
        "name": scenario_data['name'],
        "window_interest": window_interest,
        "window_principal": window_principal,
        "balance_at_window_end": balance_at_window_end,
        "lifetime_interest": total_interest_paid
    }

def run_comparison_engine(config_path):
    print(f"Loading configuration from {config_path}...")
    try:
        config_data = load_config(config_path)
    except FileNotFoundError:
        print("Error: Config file not found.")
        return

    print("Expanding scenarios...")
    scenarios = expand_scenarios(config_data)
    print(f"Generated {len(scenarios)} scenarios based on branching logic.\n")
    
    results = []
    for sc in scenarios:
        res = calculate_mortgage(sc)
        results.append(res)
        
    # Find the best window interest (lowest)
    min_window_interest = min(r['window_interest'] for r in results)
    
    # Print Table
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
        
        # Truncate name if too long
        display_name = (name[:42] + '..') if len(name) > 42 else name
        
        print(f"{display_name:<45} | ${w_int:<11,.2f} | ${w_prin:<11,.2f} | ${bal:<11,.2f} | ${l_int:<11,.2f} {cheaper_mark}")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'mortgage_config.json')
    run_comparison_engine(config_path)
