from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from . import models, schemas
from datetime import datetime, timedelta
from typing import List, Optional

def create_telemetry(db: Session, telemetry: schemas.TelemetryCreate) -> models.Telemetry:
    """Create new telemetry entry"""
    is_healthy = (
        telemetry.battery_level > 20 and
        -10 <= telemetry.temperature <= 50 and
        telemetry.signal_strength > -90
    )
    
    db_telemetry = models.Telemetry(
        **telemetry.model_dump(),
        is_healthy=is_healthy
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

def get_telemetry(db: Session, telemetry_id: int) -> Optional[models.Telemetry]:
    """Get telemetry by ID"""
    return db.query(models.Telemetry).filter(models.Telemetry.id == telemetry_id).first()

def get_telemetries(db: Session, skip: int = 0, limit: int = 100, satellite_id: Optional[str] = None) -> List[models.Telemetry]:
    """Get list of telemetries with optional filtering"""
    query = db.query(models.Telemetry)
    if satellite_id:
        query = query.filter(models.Telemetry.satellite_id == satellite_id)
    return query.order_by(desc(models.Telemetry.timestamp)).offset(skip).limit(limit).all()

def get_latest_telemetry(db: Session, satellite_id: str) -> Optional[models.Telemetry]:
    """Get latest telemetry for a satellite"""
    return db.query(models.Telemetry).filter(models.Telemetry.satellite_id == satellite_id).order_by(desc(models.Telemetry.timestamp)).first()

def get_satellite_health(db: Session, satellite_id: str) -> dict:
    """Get health status of a satellite"""
    latest = get_latest_telemetry(db, satellite_id)
    if not latest:
        return {"satellite_id": satellite_id, "status": "unknown", "latest_telemetry": None, "message": "No telemetry data available"}
    
    time_diff = datetime.now(latest.timestamp.tzinfo) - latest.timestamp
    is_recent = time_diff < timedelta(minutes=5)
    
    if not is_recent:
        status = "stale"
        message = f"Last contact {time_diff.seconds // 60} minutes ago"
    elif latest.is_healthy:
        status = "healthy"
        message = "All systems nominal"
    else:
        status = "warning"
        issues = []
        if latest.battery_level <= 20:
            issues.append("low battery")
        if latest.temperature < -10 or latest.temperature > 50:
            issues.append("temperature out of range")
        if latest.signal_strength <= -90:
            issues.append("weak signal")
        message = f"Issues detected: {', '.join(issues)}"
    
    return {"satellite_id": satellite_id, "status": status, "latest_telemetry": latest, "message": message}

def get_statistics(db: Session, satellite_id: str) -> dict:
    """Get statistics for a satellite"""
    query = db.query(
        func.count(models.Telemetry.id).label('total_records'),
        func.avg(models.Telemetry.battery_level).label('avg_battery'),
        func.avg(models.Telemetry.temperature).label('avg_temperature'),
        func.min(models.Telemetry.altitude).label('min_altitude'),
        func.max(models.Telemetry.altitude).label('max_altitude')
    ).filter(models.Telemetry.satellite_id == satellite_id)
    
    result = query.first()
    return {
        "satellite_id": satellite_id,
        "total_records": result.total_records or 0,
        "avg_battery": round(result.avg_battery, 2) if result.avg_battery else 0,
        "avg_temperature": round(result.avg_temperature, 2) if result.avg_temperature else 0,
        "min_altitude": round(result.min_altitude, 2) if result.min_altitude else 0,
        "max_altitude": round(result.max_altitude, 2) if result.max_altitude else 0
    }
