"""
Telemetry data models for Project AEGIS.

This module contains high-frequency sensor data structures.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class VehicleTelemetry(BaseModel):
    """High-frequency sensor data."""

    vehicle_id: str
    timestamp: datetime

    # Location & Movement
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    speed_kmh: float = Field(default=0.0, ge=0, description="Speed in km/h")
    odometer_km: float = Field(..., ge=0, description="Total distance traveled in km")

    # Key Metrics for Failure Scenarios
    engine_temp_celsius: float = Field(..., ge=-40, le=150, description="Engine temperature")
    battery_voltage: float = Field(..., ge=0, le=30, description="Battery voltage in volts")
    fuel_level_percent: float = Field(..., ge=0, le=100, description="Fuel level percentage")

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "timestamp": "2026-02-10T14:32:01.000Z",
                "latitude": 37.7749,
                "longitude": -122.4194,
                "speed_kmh": 65.5,
                "engine_temp_celsius": 92.5,
                "battery_voltage": 13.8,
                "fuel_level_percent": 75.0,
            }
        }
    }
