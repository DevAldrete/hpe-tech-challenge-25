"""
Data models for Project AEGIS.

This package contains all Pydantic models for vehicle telemetry, alerts,
emergencies, and dispatch.
"""

# Enums
from .enums import (
    AlertSeverity,
    FailureCategory,
    FailureScenario,
    OperationalStatus,
    VehicleType,
)

# Emergency models
from .emergency import (
    EMERGENCY_UNITS_DEFAULTS,
    Emergency,
    EmergencySeverity,
    EmergencyStatus,
    EmergencyType,
    UnitsRequired,
)

# Dispatch models
from .dispatch import Dispatch, DispatchedUnit, VehicleStatusSnapshot

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
    # Emergency
    "EMERGENCY_UNITS_DEFAULTS",
    "Emergency",
    "EmergencySeverity",
    "EmergencyStatus",
    "EmergencyType",
    "UnitsRequired",
    # Dispatch
    "Dispatch",
    "DispatchedUnit",
    "VehicleStatusSnapshot",
    # Vehicle
    "Location",
    "Vehicle",
    # Telemetry
    "VehicleTelemetry",
    # Alerts
    "PredictiveAlert",
]
