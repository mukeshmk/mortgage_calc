# Mortgage Repayment Calculator

A Python-based tool to calculate mortgage repayment schedules with support for dynamic events like interest rate changes and overpayments.

## Features
*   **JSON Configuration**: Easy-to-edit `mortgage_config.json` file for loan details.
*   **Dynamic Events**:
    *   **Rate Changes**: Handles multiple interest rate changes over the loan term. (Payments are recalculated to fit the original term).
    *   **Overpayments**: Handles lump-sum overpayments at specific months. (Reduces principal and shortening the term, keeping monthly payments constant).
*   **CSV Export**: Automatically generates `mortgage_schedule.csv` with a month-by-month breakdown.
*   **Robustness**: Error logging and cross-platform path handling.

## Files
*   `mortgage_calculator.py`: The main script.
*   `mortgage_config.json`: Configuration file.
*   `mortgage_schedule.csv`: Output file (generated after run).
*   `error_log.txt`: Created if the script encounters an error.

## Usage

### 1. Configure
Edit `mortgage_config.json` to match your loan details:
```json
{
  "loan_details": {
    "principal": 425000,
    "start_rate": 4.3,
    "years": 30
  },
  "rate_changes": [
    {"month": 13, "new_rate": 3.3}
  ],
  "overpayments": [
    {"month": 20, "amount": 5000}
  ]
}
```

### 2. Run
Double-click `mortgage_calculator.py` or run via terminal:

```bash
# Using Python
python mortgage_calculator.py

# Or if using the local virtual environment
.venv\Scripts\python.exe mortgage_calculator.py
```

### 3. Analyze
Open `mortgage_schedule.csv` in Excel or Google Sheets to view the full amortization schedule.
