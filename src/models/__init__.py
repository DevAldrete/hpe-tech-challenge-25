"""
Data models for Project AEGIS.

This package contains all Pydantic models for vehicle telemetry and alerts.
"""

# Enums
from .enums import (
    AlertSeverity,
    FailureCategory,
    FailureScenario,
    OperationalStatus,
    VehicleType,
)

# Vehicle models
from .vehicle import Location, Vehicle

# Telemetry models
from .telemetry import VehicleTelemetry

# Alert models
from .alerts import PredictiveAlert

__all__ = [
    # Enums
    "AlertSeverity",
    "FailureCategory",
    "FailureScenario",
    "OperationalStatus",
    "VehicleType",
    # Vehicle
    "Location",
    "Vehicle",
    # Telemetry
    "VehicleTelemetry",
    # Alerts
    "PredictiveAlert",
]
