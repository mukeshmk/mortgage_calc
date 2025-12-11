from fastapi import FastAPI
from typing import List, Any
import sys
import os

# Add the src directory to sys.path so we can import mortgage_lib
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from mortgage_lib.models import ScenarioConfig
from mortgage_lib.scenarios import expand_scenarios
from mortgage_lib.calculation import calculate_mortgage

app = FastAPI(title="Mortgage Calculator API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/calculate")
def calculate(config: ScenarioConfig) -> List[Any]:
    """
    Calculates mortgage scenarios based on the provided configuration.
    """
    expanded_scenarios = expand_scenarios(config)
    results = []
    
    # We might want to avoid returning the full schedule in the API if it's too big, 
    # but for now I'll include it or maybe make it optional in the query params?
    # The user didn't specify, so I'll include it.
    
    for scenario in expanded_scenarios:
        res = calculate_mortgage(scenario, return_schedule=True)
        results.append(res)
        
    return results

if __name__ == "__main__":
    import uvicorn
    # If run directly
    uvicorn.run(app, host="0.0.0.0", port=8000)
