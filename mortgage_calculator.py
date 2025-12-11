import csv
import json
import math

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

def calculate_mortgage(json_data):
    """
    Simulates the mortgage month-by-month based on configuration.
    """
    loan_details = json_data['loan_details']
    original_principal = loan_details['principal']
    current_balance = original_principal
    current_rate = loan_details['start_rate']
    total_years = loan_details['years']
    
    # Pre-process events for easier lookup
    rate_changes = {item['month']: item['new_rate'] for item in json_data.get('rate_changes', [])}
    overpayments = {item['month']: item['amount'] for item in json_data.get('overpayments', [])}
    
    total_months_originally_planned = total_years * 12
    months_remaining = total_months_originally_planned
    
    print(f"Starting Mortgage Simulation:")
    print(f" Principal: ${original_principal:,.2f}")
    print(f" Start Rate: {current_rate}%")
    print(f" Term: {total_years} years ({total_months_originally_planned} months)")
    print("-" * 50)

    # Initial monthly payment calculation
    monthly_payment = calculate_monthly_payment(current_balance, current_rate, total_years)
    print(f"Initial Monthly Payment: ${monthly_payment:,.2f}")

    total_interest_paid = 0
    total_amount_paid = 0
    month = 1
    
    # Store monthly records for CSV
    schedule_data = []
    
    while current_balance > 0.01: # Use small epsilon for float comparison logic
        start_balance = current_balance
        overpayment_amount = 0
        rate_changed = False
        
        # 1. Check for Rate Change
        if month in rate_changes:
            new_rate = rate_changes[month]
            print(f"Month {month}: Rate adjusted to {new_rate}% (from {current_rate}%)")
            current_rate = new_rate
            rate_changed = True
            
            # Recalculate minimum required monthly payment
            # Based on current balance over REMAINING planned months
            remaining_term_months = total_months_originally_planned - (month - 1)
            
            monthly_payment = calculate_monthly_payment(current_balance, current_rate, remaining_term_months / 12)
            print(f"  -> New Monthly Payment: ${monthly_payment:,.2f}")

        # 2. Calculate Interest
        monthly_interest_rate = current_rate / 100 / 12
        interest_payment = current_balance * monthly_interest_rate
        total_interest_paid += interest_payment
        
        # 3. Check for Overpayments
        if month in overpayments:
            overpayment_amount = overpayments[month]
            print(f"Month {month}: Overpayment of ${overpayment_amount:,.2f} processed")
            current_balance -= overpayment_amount
            total_amount_paid += overpayment_amount
            
            if current_balance <= 0:
                # Handle payoff via overpayment
                # We record this state but principal component below will be 0 or adjusted
                pass

        # 4. Process Regular Payment
        amount_to_pay = monthly_payment
        principal_component = 0
        
        if current_balance > 0:
             principal_component = amount_to_pay - interest_payment
             
             # Handle case where remaining balance is less than the principal component
             if current_balance < principal_component:
                  amount_to_pay = current_balance + interest_payment
                  principal_component = current_balance
             
             current_balance -= principal_component
             total_amount_paid += amount_to_pay
        
        # Record data for this month
        schedule_data.append({
            "Month": month,
            "Rate (%)": current_rate,
            "Start Balance": start_balance,
            "Monthly Payment": amount_to_pay,
            "Interest Paid": interest_payment,
            "Principal Paid": principal_component,
            "Overpayment": overpayment_amount,
            "End Balance": max(0, current_balance)
        })

        if current_balance <= 0.001: 
             break
             
        month += 1
        
        # Safety break
        if month > total_months_originally_planned * 2: 
            print("Error: Mortgage not paid off in double the time (something is wrong).")
            break

    print("-" * 50)
    print("MORTGAGE SUMMARY")
    print(f"Original Principal: ${original_principal:,.2f}")
    print(f"Total Interest Paid: ${total_interest_paid:,.2f}")
    print(f"Total Amount Paid:  ${total_amount_paid:,.2f}")
    
    # Time Savings Calculation
    final_month = month
    total_months_orig = total_months_originally_planned
    
    years_taken = final_month // 12
    months_taken = final_month % 12
    
    months_saved = total_months_orig - final_month
    years_saved = months_saved // 12
    rem_months_saved = months_saved % 12
    
    print(f"Time: Mortgage paid off in {years_taken} years, {months_taken} months")
    if months_saved > 0:
        print(f"Savings: {years_saved} years, {rem_months_saved} months earlier than planned.")
    else:
        print("Savings: None (Paid exactly on time or late).")
        
    # Write to CSV
    csv_file = "mortgage_schedule.csv"
    with open(csv_file, mode='w', newline='') as file:
        fieldnames = ["Month", "Rate (%)", "Start Balance", "Monthly Payment", "Interest Paid", "Principal Paid", "Overpayment", "End Balance"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        
        writer.writeheader()
        for row in schedule_data:
            # Format floats for prettier CSV? Optional, but keeping raw numbers is better for analysis.
            # Let's round to 2 decimals for readability if requested, but raw is fine. User wants to "see how... it changes".
            # Standard float output is fine.
            writer.writerow(row)
            
    print(f"\nDetailed schedule exported to '{csv_file}'")
