"""
Data models for Project AEGIS.

This package contains all Pydantic models for vehicle telemetry, alerts,
messages, and simulation configurations.
"""

# Enums
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

# Vehicle models
from .vehicle import GeoLocation, VehicleIdentity, VehicleState

# Telemetry models
from .telemetry import VehicleTelemetry

# Alert models
from .alerts import MaintenanceRecommendation, PredictiveAlert

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
