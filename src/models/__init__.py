"""
Data models for Project AEGIS.

This package contains all Pydantic models for vehicle telemetry, alerts,
messages, simulation configurations, emergencies, and dispatch.
"""

# Enums
# Alert models
from .alerts import MaintenanceRecommendation, PredictiveAlert

# Dispatch models
from .dispatch import Dispatch, DispatchedUnit, VehicleStatusSnapshot
from .emergency import (
    EMERGENCY_UNITS_DEFAULTS,
    Emergency,
    EmergencySeverity,
    EmergencyStatus,
    EmergencyType,
    UnitsRequired,
)
from .enums import (
    AlertSeverity,
    CommandType,
    FailureCategory,
    FailureScenario,
    MaintenanceUrgency,
    MessagePriority,
    MessageType,
    OperationalStatus,
    VehicleType,
)

# Message models
from .messages import (
    AlertAcknowledgmentPayload,
    CommandPayload,
    FleetStatusPayload,
    HeartbeatPayload,
    LocalDecisionPayload,
    Message,
)

# Simulation models
from .simulation import ScenarioParameters, SimulationConfig, WeatherConditions

# Telemetry models
from .telemetry import VehicleTelemetry

# Vehicle models
from .vehicle import GeoLocation, VehicleIdentity, VehicleState

__all__ = [
    # Enums
    "AlertSeverity",
    "CommandType",
    "FailureCategory",
    "FailureScenario",
    "MaintenanceUrgency",
    "MessagePriority",
    "MessageType",
    "OperationalStatus",
    "VehicleType",
    # Vehicle
    "GeoLocation",
    "VehicleIdentity",
    "VehicleState",
    # Telemetry
    "VehicleTelemetry",
    # Alerts
    "MaintenanceRecommendation",
    "PredictiveAlert",
    # Messages
    "AlertAcknowledgmentPayload",
    "CommandPayload",
    "FleetStatusPayload",
    "HeartbeatPayload",
    "LocalDecisionPayload",
    "Message",
    # Simulation
    "ScenarioParameters",
    "SimulationConfig",
    "WeatherConditions",
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
]
