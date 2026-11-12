# ⚙️ RecallRadar Backend API

Maintained by **Team Leader & Faisal**.

Powered by **FastAPI** to serve real-time automotive defect risk assessments, fleet alerts, and the interactive Time Machine simulation.

## How to Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- Interactive OpenAPI Swagger Docs: `http://localhost:8000/docs`
- ReDoc Docs: `http://localhost:8000/redoc`

## API Endpoints

- `GET /api/alerts`: List current high-risk vehicle/component clusters.
- `GET /api/timemachine/{entity_id}`: Monthly simulation data for time-slider playback.
- `GET /api/vehicles/{entity_id}`: Detailed investigation card for a specific vehicle defect.
