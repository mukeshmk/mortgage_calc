**Role:** You are an expert Python developer specializing in financial data processing.

**Goal:** Create a JSON-driven Mortgage Repayment Calculator. The script must read a configuration file (`mortgage_config.json`) to load loan details and a schedule of dynamic events (multiple rate changes and multiple overpayments) to calculate the exact amortization schedule.

**Core Logic Requirement:**
Do not use a static formula. You must implement a **month-by-month iteration loop** to accurately process state changes that occur at specific timestamps.

**Task Breakdown:**

**Task 1: JSON Input Structure**
The script must define and expect a JSON schema that allows for multiple events. Structure the input like this:

```json
{
  "loan_details": {
    "principal": 200000,
    "start_rate": 4.0,
    "years": 30
  },
  "rate_changes": [
    {"month": 13, "new_rate": 4.5},
    {"month": 37, "new_rate": 5.2}
  ],
  "overpayments": [
    {"month": 20, "amount": 5000},
    {"month": 40, "amount": 10000}
  ]
}
```

*Note: The code should handle lists of arbitrary length for `rate_changes` and `overpayments`.*

**Task 2: The Calculation Loop**
Create a function `calculate_mortgage(json_data)` that parses the input and iterates through the mortgage month-by-month. Inside the loop, follow this strict order of operations:

1.  **Check for Rate Change:** Check if the current month exists in the `rate_changes` list. If yes, update the interest rate.
      * *Recalculation:* If the rate changes, recalculate the **minimum required monthly payment** needed to pay off the *current balance* over the *remaining originally planned months*.
2.  **Calculate Interest:** Apply the current annual rate (divided by 12) to the *current* outstanding balance.
3.  **Check for Overpayments:** Check if the current month exists in the `overpayments` list. If yes, deduct this amount strictly from the Principal.
      * *Tenure Adjustment Strategy (Option A):* After an overpayment, **do not** lower the monthly payment. Keep the monthly payment amount at its current level. This will result in the principal decreasing faster, naturally shortening the mortgage tenure.
4.  **Process Regular Payment:** Deduct the regular monthly payment (minus the interest component) from the principal.
5.  **Break Condition:** If the principal balance drops to zero (or below), stop the loop immediately.

**Task 3: Reporting & Output**
The script should output a readable summary to the console:

  * **Summary:** Original Principal, Total Interest Paid, and Total Amount Paid.
  * **Time Savings:** Compare "Original Planned Tenure" vs "Actual Tenure" (e.g., "Mortgage paid off in 24 years, 5 months—saving 5 years, 7 months").
  * **Event Log:** Print a confirmation of every event processed (e.g., "Month 13: Rate adjusted to 4.5%", "Month 20: Overpayment of $5,000 processed").

**Task 4: Deliverables**

1.  Provide the Python script (using the `json` library).
2.  Provide a sample `mortgage_config.json` file that I can use to test the code immediately.
