# Branching Mortgage Comparison Engine

A powerful, modular Python tool designed to compare different mortgage scenarios side-by-side. It handles dynamic interest rate branching, allowing you to model complex "what-if" situations and find the most cost-effective mortgage option over a specific timeframe.

Now features a **Modern Web UI** (Streamlit) and a **REST API** (FastAPI) for flexible usage.

## Use Cases

This application is perfect for:
*   **Refinancing Decisions**: Compare your current rate vs. potential new rates.
*   **Variable Rate Modeling**: Unsure where rates will go? Model multiple possibilities (e.g., "What if rates drop to 3.5% vs stay at 4.5%?").
*   **Overpayment Strategies**: Analyze the impact of lump-sum or monthly overpayments on your term and total interest.
*   **Windowed Analysis**: Focus the cost comparison on a specific period (e.g., the 2-year fixed term of a new deal) to see exactly how much you save or lose during that specific contract period.

## Key Features

*   **Branching Scenarios**: Automatically generates multiple scenarios when you provide a list of potential interest rates (e.g., `[2.8, 2.2]`). It creates a decision tree of all possible outcomes.
*   **Interactive UI**: A Streamlit-based web interface to easily input loan details, adjust settings, and visualize results with interactive charts.
*   **REST API**: A FastAPI backend to integrate the calculation engine into other workflows.
*   **Detailed Reporting**: Exports comprehensive CSV schedules and Excel comparison sheets highlighting exactly when and where scenarios differ.
*   **Modular Design**: Core logic is separated into a reusable library `src/mortgage_lib`.

## Installation

1.  **Clone/Download** the repository.
2.  **Install Dependencies**:
    ```bash
    pip install fastapi uvicorn streamlit pandas pydantic openpyxl
    ```

## How to Run

### 1. The Interactive UI (Recommended)
The easiest way to use the tool is via the Streamlit web interface:

```bash
streamlit run src/ui/app.py
```
*   This will open your browser to `http://localhost:8501`.
*   You can enter loan details manually or upload a configuration JSON file.
*   **Visuals**: View interactive comparisons of "Balance Over Time" and "Interest Paid".

### 2. The REST API
To run the calculation engine as a server:

```bash
uvicorn src.api.main:app --reload
```
*   **Documentation**: Go to `http://localhost:8000/docs` to see the Swagger UI.
*   **Endpoint**: POST `http://localhost:8000/calculate` with your JSON configuration.

### 3. Command Line Verification
To verify the engine against a config file without a UI:

```bash
python verify_refactor.py
```
*(This script runs the engine using `mortgage_config.json`)*

## Configuration & Scenarios

The power of this tool lies in its **Branching Scenario** capability.

### Configuration Format (`mortgage_config.json`)

```json
{
    "base_loan": {
        "principal": 425000,
        "start_rate": 4.3,
        "years": 30
    },
    "rate_changes": [
        {
            "month": 13,
            "new_rate": [3.3, 2.8] 
        }
    ],
    "analysis_settings": {
        "window_start_month": 13,
        "window_end_month": 61
    }
}
```

### Understanding Scenarios

1.  **Base Scenario**: Starts with the initial loan details.
2.  **Rate Changes**: You define events at specific months.
    *   **Single Rate**: `"new_rate": 3.5` -> The timeline continues with this new rate.
    *   **Multiple Rates (Branching)**: `"new_rate": [3.3, 2.8]` -> The timeline **splits**.
        *   Path A: Rate becomes 3.3% at Month 13.
        *   Path B: Rate becomes 2.8% at Month 13.
3.  **Recursive Branching**: If you have another list of rates later (e.g., at Month 60), *every active branch* will split again. This allows you to model decision trees like:
    *   *Path A1*: Rate 3.3% -> then drops to 2.5%
    *   *Path A2*: Rate 3.3% -> then rises to 4.0%
    *   *Path B1*: Rate 2.8% -> then stays flat...

### Comparison Metrics

*   **Window Interest**: Total interest paid within your specified start and end months.
*   **Lifetime Interest**: Total interest paid over the life of the loan.
*   **Balance @ Window End**: How much principal remains at the end of your analysis window.

## Project Structure

*   `src/mortgage_lib`: Core calculation and logic library.
*   `src/api`: FastAPI application.
*   `src/ui`: Streamlit web application.
