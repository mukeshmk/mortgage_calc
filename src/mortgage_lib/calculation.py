import math
from typing import List, Dict, Any
from .models import SingleScenario

def calculate_monthly_payment(principal: float, annual_rate: float, years: float) -> float:
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

def calculate_mortgage(scenario: SingleScenario, return_schedule: bool = False, verbose: bool = False) -> Dict[str, Any]:
    """
    Simulates the mortgage.
    If return_schedule is True, includes the full monthly data list in the return dict.
    """
    loan_details = scenario.loan_details
    original_principal = loan_details.principal
    current_balance = original_principal
    current_rate = loan_details.start_rate
    total_years = loan_details.years
    
    analysis_window = scenario.analysis_settings
    window_start = analysis_window.window_start_month if analysis_window else 1
    window_end = analysis_window.window_end_month if analysis_window else 12
    
    # helper for lookups
    rate_changes_map = {item.month: item.new_rate for item in scenario.rate_changes}
    overpayments_map = {item.month: item.amount for item in scenario.overpayments}
    
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
        print(f"\n--- Simulating: {scenario.name} ---")
        print(f"Start Rate: {current_rate}%, Window: M{window_start}-{window_end}")

    while current_balance > 0.01:
        start_balance = current_balance
        overpayment_amount = 0
        
        if month in rate_changes_map:
            new_rate = rate_changes_map[month]
            if verbose: print(f"  [Event] Month {month}: Rate change {current_rate}% -> {new_rate}%")
            current_rate = new_rate
            # Recalculate payment
            remaining_term_months = total_months_originally_planned - (month - 1)
            # Guard against negative or zero remaining term if scenario goes somehow beyond
            if remaining_term_months <= 0:
                 monthly_payment = current_balance # Force pay off
            else:
                 monthly_payment = calculate_monthly_payment(current_balance, current_rate, remaining_term_months / 12)

        monthly_interest_rate = current_rate / 100 / 12
        interest_payment = current_balance * monthly_interest_rate
        total_interest_paid += interest_payment
        
        if month in overpayments_map:
            overpayment_amount = overpayments_map[month]
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
            cumulative_total_paid += amount_to_pay + overpayment_amount if month in overpayments_map else amount_to_pay 
            
            schedule_data.append({
                "Month": month,
                "Rate (%)": current_rate,
                "Start Balance": round(start_balance, 2),
                "Monthly Payment": round(amount_to_pay, 2),
                "Interest Paid": round(interest_payment, 2),
                "Principal Paid": round(principal_component + overpayment_amount, 2), 
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
        "name": scenario.name,
        "window_interest": window_interest,
        "window_principal": window_principal,
        "balance_at_window_end": balance_at_window_end,
        "lifetime_interest": total_interest_paid
    }
    
    if return_schedule:
        result["schedule"] = schedule_data
        
    return result
