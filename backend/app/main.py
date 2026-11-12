from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import alerts, timemachine, vehicles

app = FastAPI(
    title="RecallRadar API",
    description="Automotive Defect Early Warning & Recall Prediction Service",
    version="1.0.0"
)

# Enable CORS for React frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Route Handlers
app.include_router(alerts.router, prefix="/api")
app.include_router(timemachine.router, prefix="/api")
app.include_router(vehicles.router, prefix="/api")


@app.get("/")
def root():
    return {
        "service": "RecallRadar API",
        "status": "operational",
        "docs_url": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
