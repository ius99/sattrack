from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class Telemetry(Base):
    """Satellite telemetry data model"""
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    satellite_id = Column(String, index=True, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Position data
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude = Column(Float, nullable=False)
    
    # System health
    battery_level = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    signal_strength = Column(Float, nullable=False)
    
    # Status
    is_healthy = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<Telemetry(satellite={self.satellite_id}, time={self.timestamp})>"
