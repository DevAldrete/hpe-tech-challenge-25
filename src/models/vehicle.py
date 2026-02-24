"""
Vehicle identity and state models for Project AEGIS.

This module contains data models for vehicle information and operational state.
"""

from pydantic import BaseModel, Field

from .enums import OperationalStatus, VehicleType


class Location(BaseModel):
    """Geographic location."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")


class Vehicle(BaseModel):
    """Vehicle core model."""

    vehicle_id: str = Field(..., description="Unique ID like AMB-001 or FIRE-042")
    vehicle_type: VehicleType = Field(..., description="Type of vehicle")
    operational_status: OperationalStatus = Field(
        default=OperationalStatus.IDLE, description="Current status"
    )
    location: Location | None = Field(None, description="Current location")

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "vehicle_type": "ambulance",
                "operational_status": "en_route",
                "location": {
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                },
            }
        }
    }
