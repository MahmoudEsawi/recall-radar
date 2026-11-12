from typing import List, Optional
from fastapi import APIRouter, Query
from app.schemas import VehicleAlert
from app.mock_data import MOCK_ALERTS

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("", response_model=List[VehicleAlert])
def get_alerts(
    category: Optional[str] = Query(None, description="Filter by risk category: CRITICAL, HIGH, MODERATE"),
    make: Optional[str] = Query(None, description="Filter by make (e.g. FORD, HONDA)")
):
    """
    Returns prioritized list of vehicle defect alerts based on current risk scores.
    """
    alerts = MOCK_ALERTS
    if category:
        alerts = [a for a in alerts if a["risk_category"].upper() == category.upper()]
    if make:
        alerts = [a for a in alerts if a["make"].upper() == make.upper()]
    return alerts
