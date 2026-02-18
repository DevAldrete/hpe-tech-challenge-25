"""
Data models for Project AEGIS.

This package contains all Pydantic models for vehicle telemetry, alerts,
messages, and simulation configurations.
"""

# Enums
# Alert models
from .alerts import MaintenanceRecommendation, PredictiveAlert
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
]
