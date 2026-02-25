"""
Enumerations for Project AEGIS.

This module contains all enum definitions used throughout the system.
"""

from enum import Enum


class VehicleType(str, Enum):
    """Type of emergency vehicle."""

    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"
    POLICE = "police"


class OperationalStatus(str, Enum):
    """Current operational status of a vehicle."""

    IDLE = "idle"  # At station, ready for dispatch
    EN_ROUTE = "en_route"  # Responding to emergency
    ON_SCENE = "on_scene"  # At emergency location
    RETURNING = "returning"  # Returning to station
    MAINTENANCE = "maintenance"  # Scheduled maintenance
    OUT_OF_SERVICE = "out_of_service"  # Broken/unavailable
    OFFLINE = "offline"  # Not connected to system


class AlertSeverity(str, Enum):
    """Severity level of predictive alerts."""

    CRITICAL = "critical"  # Immediate action required
    WARNING = "warning"  # Action needed soon
    INFO = "info"  # Informational only


class FailureCategory(str, Enum):
    """Category of vehicle component failure."""

    ENGINE = "engine"
    ELECTRICAL = "electrical"
    FUEL = "fuel"
    OTHER = "other"


class FailureScenario(str, Enum):
    """Predefined failure modes for simulation."""

    ENGINE_OVERHEAT = "engine_overheat"
    BATTERY_DEGRADATION = "battery_degradation"
    FUEL_LEAK = "fuel_leak"
