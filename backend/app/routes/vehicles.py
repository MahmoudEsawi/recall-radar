from fastapi import APIRouter, HTTPException
from app.schemas import VehicleAlert
from app.mock_data import MOCK_ALERTS

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("/{entity_id}", response_model=VehicleAlert)
def get_vehicle_defect_detail(entity_id: str):
    """
    Returns full diagnostics, feature breakdown, and official recall status for a specific vehicle defect.
    """
    for alert in MOCK_ALERTS:
        if alert["entity_id"] == entity_id:
            return alert
    raise HTTPException(status_code=404, detail="Vehicle entity not found")
