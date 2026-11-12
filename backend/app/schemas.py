from typing import List, Optional
from pydantic import BaseModel


class RiskFactor(BaseModel):
    factor: str
    detail: str
    impact: str  # Critical, High, Moderate


class TimelinePoint(BaseModel):
    month: str
    complaints: int
    risk_score: float


class OfficialRecall(BaseModel):
    recalled: bool
    recall_date: Optional[str] = None
    campaign_id: Optional[str] = None
    defect_summary: Optional[str] = None


class VehicleAlert(BaseModel):
    entity_id: str
    make: str
    model: str
    year: int
    component: str
    as_of_date: str
    risk_score: float
    risk_category: str  # CRITICAL, HIGH, MODERATE, LOW
    predicted_recall_within_12m: bool
    lead_time_months: Optional[int] = None
    complaint_count: int
    top_risk_factors: List[RiskFactor]
    official_recall: Optional[OfficialRecall] = None


class TimeMachineData(BaseModel):
    entity_id: str
    make: str
    model: str
    year: int
    component: str
    first_detected_date: str
    official_recall_date: Optional[str] = None
    lead_time_months: Optional[int] = None
    monthly_timeline: List[TimelinePoint]
    top_risk_factors: List[RiskFactor]
