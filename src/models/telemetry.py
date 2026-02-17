"""
Telemetry data models for Project AEGIS.

This module contains high-frequency sensor data structures (1 Hz telemetry).
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.models.vehicle import GeoLocation


class VehicleTelemetry(BaseModel):
    """High-frequency sensor data captured every second (1 Hz)."""

    vehicle_id: str
    timestamp: datetime
    sequence_number: int = Field(
        ..., description="Monotonic counter for message ordering and deduplication"
    )

    # Location & Movement
    location: GeoLocation
    odometer_km: float = Field(..., ge=0, description="Total distance traveled in km")

    # Engine & Powertrain
    engine_temp_celsius: float = Field(..., ge=-40, le=150, description="Engine temperature")
    engine_rpm: int = Field(..., ge=0, le=8000, description="Engine RPM")
    coolant_temp_celsius: float = Field(..., ge=-40, le=150, description="Coolant temperature")
    oil_pressure_psi: float = Field(..., ge=0, le=100, description="Oil pressure in PSI")
    oil_temp_celsius: float = Field(..., ge=-40, le=200, description="Oil temperature")
    transmission_temp_celsius: float = Field(
        ..., ge=-40, le=150, description="Transmission temperature"
    )
    throttle_position_percent: float = Field(
        ..., ge=0, le=100, description="Throttle position percentage"
    )

    # Electrical System
    battery_voltage: float = Field(..., ge=0, le=30, description="Battery voltage in volts")
    battery_current_amps: float = Field(
        ..., description="Battery current (+ charging, - discharging)"
    )
    alternator_voltage: float = Field(..., ge=0, le=30, description="Alternator output voltage")
    battery_state_of_charge_percent: float = Field(
        ..., ge=0, le=100, description="Battery state of charge"
    )
    battery_health_percent: float = Field(..., ge=0, le=100, description="Battery health indicator")

    # Fuel System
    fuel_level_percent: float = Field(..., ge=0, le=100, description="Fuel level percentage")
    fuel_level_liters: float = Field(..., ge=0, description="Fuel level in liters")
    fuel_consumption_lph: float = Field(
        default=0.0, ge=0, description="Fuel consumption in liters per hour"
    )
    fuel_economy_kml: float | None = Field(None, ge=0, description="Fuel economy in km per liter")

    # Braking System
    brake_pad_thickness_mm: dict[str, float] = Field(
        default_factory=lambda: {
            "front_left": 10.0,
            "front_right": 10.0,
            "rear_left": 10.0,
            "rear_right": 10.0,
        },
        description="Brake pad thickness per wheel in millimeters",
    )
    brake_fluid_level_percent: float = Field(
        ..., ge=0, le=100, description="Brake fluid level percentage"
    )
    brake_temp_celsius: dict[str, float] = Field(
        default_factory=dict, description="Brake temperature per wheel"
    )
    abs_active: bool = Field(default=False, description="ABS system currently active")

    # Tires
    tire_pressure_psi: dict[str, float] = Field(
        default_factory=lambda: {
            "front_left": 80.0,
            "front_right": 80.0,
            "rear_left": 80.0,
            "rear_right": 80.0,
        },
        description="Tire pressure per wheel in PSI",
    )
    tire_temp_celsius: dict[str, float] = Field(
        default_factory=dict, description="Tire temperature per wheel"
    )

    # Suspension & Chassis
    suspension_travel_mm: dict[str, float] = Field(
        default_factory=dict, description="Suspension travel per wheel"
    )
    vibration_g_force: dict[str, float] = Field(
        default_factory=lambda: {"x": 0.0, "y": 0.0, "z": 0.0},
        description="Vibration acceleration in G-force (x, y, z axes)",
    )

    # Environmental
    cabin_temp_celsius: float = Field(default=20.0, description="Interior cabin temperature")
    exterior_temp_celsius: float = Field(default=20.0, description="Exterior temperature")
    humidity_percent: float = Field(default=50.0, ge=0, le=100, description="Humidity percentage")

    # Emergency Equipment Status
    siren_active: bool = Field(default=False, description="Emergency siren active")
    lights_active: bool = Field(default=False, description="Emergency lights active")
    equipment_status: dict[str, dict[str, Any]] = Field(
        default_factory=dict,
        description="Type-specific equipment status (defibrillator, water pump, etc.)",
    )

    # Diagnostic Trouble Codes
    active_dtc_codes: list[str] = Field(
        default_factory=list, description="Active diagnostic trouble codes"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "timestamp": "2026-02-10T14:32:01.000Z",
                "sequence_number": 12345,
                "location": {
                    "latitude": 37.7749,
                    "longitude": -122.4194,
                    "speed_kmh": 65.5,
                    "heading": 45.0,
                },
                "odometer_km": 45678.9,
                "engine_temp_celsius": 92.5,
                "engine_rpm": 2500,
                "battery_voltage": 13.8,
                "fuel_level_percent": 75.0,
                "fuel_level_liters": 30.0,
                "tire_pressure_psi": {
                    "front_left": 80.0,
                    "front_right": 80.0,
                    "rear_left": 80.0,
                    "rear_right": 80.0,
                },
            }
        }
    }
