from fastapi import APIRouter, HTTPException
from app.schemas import TimeMachineData
from app.mock_data import MOCK_TIME_MACHINE

router = APIRouter(prefix="/timemachine", tags=["Time Machine"])


@router.get("/{entity_id}", response_model=TimeMachineData)
def get_time_machine_simulation(entity_id: str):
    """
    Returns month-by-month historical complaint buildup and risk score evolution
    for the interactive 'Time Machine' slider presentation.
    """
    if entity_id not in MOCK_TIME_MACHINE:
        # Default fallback to Ford Explorer simulation
        return MOCK_TIME_MACHINE["ford_explorer_2016_suspension"]
    return MOCK_TIME_MACHINE[entity_id]
