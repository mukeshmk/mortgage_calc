import copy
from typing import List
from .models import ScenarioConfig, SingleScenario, SingleRateChange

def expand_scenarios(config: ScenarioConfig) -> List[SingleScenario]:
    """
    Parses the configuration and branches scenarios whenever a rate change
    has a list of options.
    Returns a list of complete scenario objects.
    """
    # Create the base scenario structure
    # Note: We need to convert from ScenarioConfig to SingleScenario structure
    # But recursively handling the branching
    
    # We will use a dictionary-like approach for recursion simplicity, 
    # then convert to objects at the end, or work with objects directly.
    # Working with objects directly is safer.
    
    base_scenario = SingleScenario(
        name="Base Scenario", # Will be updated
        loan_details=config.base_loan,
        rate_changes=[], 
        overpayments=config.overpayments,
        analysis_settings=config.analysis_settings
    )

    # We need the list of RateChange objects from the config
    raw_rate_changes = config.rate_changes
    
    def build_branches(current_scenario: SingleScenario, remaining_changes) -> List[SingleScenario]:
        if not remaining_changes:
            return [current_scenario]
        
        next_change = remaining_changes[0]
        rest_changes = remaining_changes[1:]
        
        branches = []
        
        # Check if next_change.new_rate is a list
        if isinstance(next_change.new_rate, list):
            # Branching
            for rate_option in next_change.new_rate:
                # Deepcopy current scenario
                new_branch = current_scenario.model_copy(deep=True)
                # Append the single event
                new_branch.rate_changes.append(
                    SingleRateChange(month=next_change.month, new_rate=rate_option)
                )
                # Update name
                new_branch.name += f" -> {rate_option}% @ M{next_change.month}"
                
                branches.extend(build_branches(new_branch, rest_changes))
        else:
            # No branching
            # We can modify current_scenario if we are sure it's a copy or just pass it along?
            # Ideally we treat it immutably or careful copies.
            # Since we come from a path where we might have branched, we should modify *this* branch's copy.
            # But wait, if we are in the "else" block, we didn't fork *here*, 
            # but we might be iterating inside a parent's loop.
            # To be safe, we should probably append to the current object.
            # However, if 'current_scenario' is reused (it is passed by reference), we must be careful.
            # But in build_branches, 'current_scenario' is passed in.
            
            # Use model_copy to be safe if we are modifying it.
            # Actually, let's just modify it if it's unique to this path.
            # But Python references...
            # Let's just blindly copy to be safe, optimization comes later.
            current_scenario_copy = current_scenario.model_copy(deep=True)
            
            current_scenario_copy.rate_changes.append(
                SingleRateChange(month=next_change.month, new_rate=next_change.new_rate)
            )
            branches.extend(build_branches(current_scenario_copy, rest_changes))
            
        return branches

    base_scenario.name = "Scenario" 
    expanded_scenarios = build_branches(base_scenario, raw_rate_changes)
    return expanded_scenarios
