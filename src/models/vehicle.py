"""
Vehicle identity and state models for Project AEGIS.

This module contains data models for vehicle information and operational state.
"""

from datetime import datetime

from pydantic import BaseModel, Field

from .enums import OperationalStatus, VehicleType


class GeoLocation(BaseModel):
    """Geographic location with GPS data."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")
    altitude: float = Field(
        default=0.0, description="Altitude in meters above sea level"
    )
    accuracy: float = Field(default=10.0, description="GPS accuracy in meters")
    heading: float = Field(
        default=0.0, ge=0, le=360, description="Direction in degrees"
    )
    speed_kmh: float = Field(default=0.0, ge=0, description="Speed in km/h")
    timestamp: datetime

    model_config = {
        "json_schema_extra": {
            "example": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "altitude": 15.5,
                "accuracy": 5.0,
                "heading": 45.0,
                "speed_kmh": 65.5,
                "timestamp": "2026-02-10T14:32:01.000Z",
            }
        }
    }


class VehicleIdentity(BaseModel):
    """Static vehicle information and equipment manifest."""

    vehicle_id: str = Field(..., description="Unique ID like AMB-001 or FIRE-042")
    vehicle_type: VehicleType
    unit_number: str = Field(..., description="Fleet unit number")
    station_id: str = Field(..., description="Home station/base identifier")
    make: str = Field(default="Ford", description="Vehicle manufacturer")
    model: str = Field(..., description="Vehicle model")
    year: int = Field(..., ge=2000, le=2030, description="Model year")
    vin: str = Field(..., description="Vehicle Identification Number")
    equipment_manifest: dict[str, str] = Field(
        default_factory=dict, description="Type-specific equipment dictionary"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "vehicle_type": "ambulance",
                "unit_number": "A1",
                "station_id": "ST-CENTRAL",
                "make": "Ford",
                "model": "F-450 Super Duty",
                "year": 2025,
                "vin": "1FDUF5HT5MEC12345",
                "equipment_manifest": {
                    "defibrillator": "Zoll X Series",
                    "stretcher": "Stryker Power-PRO",
                    "ventilator": "Philips Trilogy Evo",
                },
            }
        }
    }


class VehicleState(BaseModel):
    """Current operational state and mission context."""

    vehicle_id: str
    timestamp: datetime
    operational_status: OperationalStatus
    mission_id: str | None = Field(None, description="Current emergency/mission ID")
    assigned_crew: list[str] = Field(
        default_factory=list, description="List of crew member IDs"
    )
    crew_count: int = Field(default=0, ge=0, description="Number of personnel on board")
    destination: GeoLocation | None = Field(None, description="Target location")
    eta_seconds: int | None = Field(
        None, ge=0, description="Estimated time to destination"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "timestamp": "2026-02-10T14:32:00.000Z",
                "operational_status": "en_route",
                "mission_id": "MISSION-2026-02-10-001",
                "crew_count": 3,
                "assigned_crew": ["crew_001", "crew_002", "crew_003"],
                "destination": {
                    "latitude": 37.8049,
                    "longitude": -122.4194,
                    "altitude": 0.0,
                },
                "eta_seconds": 420,
            }
        }
    }
