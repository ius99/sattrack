from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TelemetryBase(BaseModel):
    """Base telemetry schema"""
    satellite_id: str = Field(..., example="SAT-001")
    latitude: float = Field(..., ge=-90, le=90, example=43.6532)
    longitude: float = Field(..., ge=-180, le=180, example=-79.3832)
    altitude: float = Field(..., gt=0, example=550.5)
    battery_level: float = Field(..., ge=0, le=100, example=87.5)
    temperature: float = Field(..., example=22.3)
    signal_strength: float = Field(..., example=-65.2)

class TelemetryCreate(TelemetryBase):
    """Schema for creating telemetry"""
    pass

class TelemetryResponse(TelemetryBase):
    """Schema for telemetry response"""
    id: int
    timestamp: datetime
    is_healthy: bool

    class Config:
        from_attributes = True

class HealthStatus(BaseModel):
    """Health status response"""
    satellite_id: str
    status: str
    latest_telemetry: Optional[TelemetryResponse]
    message: str
