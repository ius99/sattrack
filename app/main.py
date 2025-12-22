from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from . import models, schemas, crud
from .database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="SatTrack API",
    description="Satellite Telemetry Tracking System",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "SatTrack API - Satellite Telemetry System", "docs": "/docs", "version": "1.0.0"}

@app.post("/telemetry", response_model=schemas.TelemetryResponse, status_code=201)
def create_telemetry(telemetry: schemas.TelemetryCreate, db: Session = Depends(get_db)):
    return crud.create_telemetry(db=db, telemetry=telemetry)

@app.get("/telemetry", response_model=List[schemas.TelemetryResponse])
def list_telemetry(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=1000), satellite_id: Optional[str] = None, db: Session = Depends(get_db)):
    return crud.get_telemetries(db, skip=skip, limit=limit, satellite_id=satellite_id)

@app.get("/telemetry/{telemetry_id}", response_model=schemas.TelemetryResponse)
def get_telemetry(telemetry_id: int, db: Session = Depends(get_db)):
    telemetry = crud.get_telemetry(db, telemetry_id=telemetry_id)
    if telemetry is None:
        raise HTTPException(status_code=404, detail="Telemetry not found")
    return telemetry

@app.get("/satellite/{satellite_id}/latest", response_model=schemas.TelemetryResponse)
def get_latest_telemetry(satellite_id: str, db: Session = Depends(get_db)):
    telemetry = crud.get_latest_telemetry(db, satellite_id=satellite_id)
    if telemetry is None:
        raise HTTPException(status_code=404, detail=f"No telemetry found for satellite {satellite_id}")
    return telemetry

@app.get("/satellite/{satellite_id}/health", response_model=schemas.HealthStatus)
def get_satellite_health(satellite_id: str, db: Session = Depends(get_db)):
    return crud.get_satellite_health(db, satellite_id=satellite_id)

@app.get("/satellite/{satellite_id}/stats")
def get_satellite_stats(satellite_id: str, db: Session = Depends(get_db)):
    return crud.get_statistics(db, satellite_id=satellite_id)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "SatTrack API"}
