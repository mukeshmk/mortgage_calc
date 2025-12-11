from typing import List, Union, Optional
from pydantic import BaseModel

class AnalysisSettings(BaseModel):
    window_start_month: int = 1
    window_end_month: int = 12

class LoanDetails(BaseModel):
    principal: float
    start_rate: float
    years: int

class RateChange(BaseModel):
    month: int
    new_rate: Union[float, List[float]]

class Overpayment(BaseModel):
    month: int
    amount: float

class ScenarioConfig(BaseModel):
    analysis_settings: Optional[AnalysisSettings] = None
    base_loan: LoanDetails
    rate_changes: List[RateChange] = []
    overpayments: List[Overpayment] = []

class SingleRateChange(BaseModel):
    month: int
    new_rate: float

class SingleScenario(BaseModel):
    name: str = "Base Scenario"
    loan_details: LoanDetails
    rate_changes: List[SingleRateChange] = []
    overpayments: List[Overpayment] = []
    analysis_settings: Optional[AnalysisSettings] = None
