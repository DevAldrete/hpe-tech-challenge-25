"""
Enumerations for Project AEGIS.

This module contains all enum definitions used throughout the system.
"""

from enum import Enum


class VehicleType(str, Enum):
    """Type of emergency vehicle."""

    AMBULANCE = "ambulance"
    FIRE_TRUCK = "fire_truck"


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
    TRANSMISSION = "transmission"
    ELECTRICAL = "electrical"
    BRAKES = "brakes"
    COOLING = "cooling"
    FUEL = "fuel"
    TIRES = "tires"
    SUSPENSION = "suspension"
    EQUIPMENT = "equipment"  # Emergency equipment


class MaintenanceUrgency(str, Enum):
    """Urgency level for maintenance recommendations."""

    IMMEDIATE = "immediate"  # Stop vehicle now
    URGENT = "urgent"  # Within 24 hours
    SCHEDULED = "scheduled"  # Within 1 week
    PREVENTIVE = "preventive"  # Next regular maintenance cycle


class MessageType(str, Enum):
    """Type of message in the communication protocol."""

    # Vehicle → Orchestrator
    TELEMETRY_UPDATE = "telemetry.update"
    HEARTBEAT = "vehicle.heartbeat"
    ALERT_GENERATED = "alert.generated"
    STATUS_CHANGE = "vehicle.status_change"
    LOCAL_DECISION = "vehicle.local_decision"

    # Orchestrator → Vehicle
    COMMAND = "vehicle.command"
    CONFIG_UPDATE = "vehicle.config_update"
    ALERT_ACKNOWLEDGE = "alert.acknowledge"
    MISSION_ASSIGNMENT = "mission.assignment"
    OVERRIDE_DECISION = "vehicle.override"

    # Orchestrator → Dashboard
    FLEET_STATUS = "fleet.status"
    ALERT_BROADCAST = "alert.broadcast"
    VEHICLE_UPDATE = "vehicle.update"


class MessagePriority(str, Enum):
    """Priority level for message delivery."""

    CRITICAL = "critical"  # Sub-second delivery needed
    HIGH = "high"  # < 1 second
    NORMAL = "normal"  # < 5 seconds
    LOW = "low"  # Best effort


class CommandType(str, Enum):
    """Type of command sent to vehicles."""

    STANDBY = "standby"  # Go to idle/ready state
    DISPATCH = "dispatch"  # Respond to emergency
    RETURN_TO_BASE = "return_to_base"  # Return to station
    MAINTENANCE_MODE = "maintenance_mode"  # Enter maintenance
    EMERGENCY_STOP = "emergency_stop"  # Immediate shutdown
    UPDATE_CONFIG = "update_config"  # Update configuration


class FailureScenario(str, Enum):
    """Predefined failure modes for simulation."""

    # Engine failures
    ENGINE_OVERHEAT = "engine_overheat"
    OIL_PRESSURE_DROP = "oil_pressure_drop"
    COOLANT_LEAK = "coolant_leak"

    # Electrical failures
    ALTERNATOR_FAILURE = "alternator_failure"
    BATTERY_DEGRADATION = "battery_degradation"
    VOLTAGE_SPIKE = "voltage_spike"

    # Brake failures
    BRAKE_PAD_WEAR_CRITICAL = "brake_pad_wear_critical"
    BRAKE_FLUID_LEAK = "brake_fluid_leak"
    ABS_MALFUNCTION = "abs_malfunction"

    # Tire failures
    TIRE_PRESSURE_LOW = "tire_pressure_low"
    TIRE_BLOWOUT = "tire_blowout"
    UNEVEN_TIRE_WEAR = "uneven_tire_wear"

    # Fuel system
    FUEL_PUMP_FAILURE = "fuel_pump_failure"
    FUEL_LEAK = "fuel_leak"
    INJECTOR_CLOG = "injector_clog"

    # Transmission
    TRANSMISSION_OVERHEAT = "transmission_overheat"
    GEAR_SLIPPAGE = "gear_slippage"

    # Equipment (vehicle-type specific)
    WATER_PUMP_FAILURE = "water_pump_failure"  # Fire truck
    LADDER_HYDRAULIC_LEAK = "ladder_hydraulic_leak"  # Fire truck
    DEFIBRILLATOR_BATTERY_LOW = "defibrillator_battery_low"  # Ambulance
    MEDICAL_OXYGEN_LOW = "medical_oxygen_low"  # Ambulance
