Role: You are an expert Python Financial Systems Architect.

Goal: Build a Branching Mortgage Comparison Engine. The system must accept a JSON configuration where specific interest rate changes can be provided as a list of options (e.g., [3.3, 2.1]). The code must automatically generate and compare all possible scenario variations based on these options.

Task Breakdown:

Task 1: Flexible JSON Schema The system must accept a JSON structure where new_rate can be either a single float OR a list of floats.

    Input Example:

JSON

{
    "analysis_settings": {
        "window_start_month": 13,
        "window_end_month": 24
    },
    "base_loan": {
        "principal": 425000,
        "start_rate": 4.3,
        "years": 30
    },
    "rate_changes": [
        { "month": 13, "new_rate": [3.3, 2.1] }, 
        { "month": 25, "new_rate": 2.8 },
        { "month": 37, "new_rate": 3.6 }
    ],
    "overpayments": [
        { "month": 13, "amount": 1800 }
    ]
}

Task 2: The "Scenario Expander" Logic (Crucial) Before calculating, you must write a pre-processing function expand_scenarios(json_data).

    Parse the rate_changes list.

    Detect any event where new_rate is a list (e.g., [3.3, 2.1]).

    Branch the Timeline: automatically generate a separate, complete scenario object for each rate in that list.

        Branch 1: Uses 3.3% at Month 13.

        Branch 2: Uses 2.1% at Month 13.

        Note: Both branches should inherit all subsequent events (like the Month 25 rate of 2.8%) unless those also branch.

    Naming: Automatically name them for the report (e.g., "Scenario - Rate Option 3.3%", "Scenario - Rate Option 2.1%").

Task 3: Windowed Calculation Iterate through the expanded list of scenarios. Calculate the metrics for the specific window defined in analysis_settings (Month 13 to 24):

    Window Interest: Total interest paid strictly between start/end months.

    Window Principal: Total principal paid strictly between start/end months.

    Balance @ End: The outstanding balance at the end of the window.

Task 4: Reporting Output a table comparing the branches side-by-side.

    Columns: Scenario Name | Window Interest | Window Principal | Balance @ Month 24 | Lifetime Interest

    Highlight: Flag which branch was cheaper during the window.

Task 5: Deliverables

    Python script with the recursive/expansion logic to handle the lists.

    The JSON file exactly as provided in the prompt example.
    