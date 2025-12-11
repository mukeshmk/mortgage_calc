# Branching Mortgage Comparison Engine

A powerful Python tool designed to compare different mortgage scenarios side-by-side. It handles dynamic interest rate branching to help you find the most cost-effective mortgage option over a specific timeframe.

## Key Features

*   **Branching Scenarios**: Automatically generates multiple scenarios when you provide a list of potential interest rates (e.g., `[2.8, 2.2]`).
*   **Windowed Analysis**: Focuses comparison on a specific period (e.g., Months 13-36) to see cost differences during critical rate periods.
*   **comparison Engine**:
    *   **Terminal Dashboard**: Instant summary table highlighting the cheapest option within your analysis window.
    *   **Smart Excel Export**: Generates `scenario_comparison.xlsx` with separate sheets for each scenario, specifically targeting months where rates differ.
    *   **Detailed CSV**: Exports the full amortization schedule of the overall cheapest scenario to `mortgage_schedule.csv`.
*   **Flexible Configuration**: Easy-to-use JSON config for loan details, rate changes, and overpayments.

## Quick Start

### 1. Configure (`mortgage_config.json`)
Define your loan parameters and analysis goals.

```json
{
    "analysis_settings": {
        "window_start_month": 13,
        "window_end_month": 36
    },
    "base_loan": {
        "principal": 425000,
        "start_rate": 4.3,
        "years": 30
    },
    "rate_changes": [
        {
            "month": 13,
            "new_rate": [3.3, 2.1]  <-- Creates 2 branches
        },
        {
            "month": 25,
            "new_rate": 2.8         <-- Applied to all active branches
        }
    ],
    "overpayments": [
        { "month": 13, "amount": 1800 }
    ]
}
```

### 2. Run the Engine
Execute the script from your terminal:

```bash
# Using the local virtual environment (recommended)
.venv\Scripts\python mortgage_calculator.py

# Or standard python
python mortgage_calculator.py
```

### 3. Analyze Results
*   **Terminal**: Check the "COMPARISON RESULTS" table for a quick win/loss analysis.
*   **`mortgage_schedule.csv`**: Full monthly breakdown of the winner.
*   **`scenario_comparison.xlsx`**: Deep dive into the differences.

## File Structure
*   `mortgage_calculator.py`: Core logic for branching, calculation, and reporting.
*   `mortgage_config.json`: User inputs and settings.
*   `walkthrough.md`: Detailed step-by-step guide.
