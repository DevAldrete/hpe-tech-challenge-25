"""
Pytest fixtures for model testing in Project AEGIS.

This module provides reusable test data fixtures for all models.
"""

from datetime import datetime, timezone

import pytest

from src.models.enums import (
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


@pytest.fixture
def sample_datetime() -> datetime:
    """Provide a consistent datetime for testing."""
    return datetime(2026, 2, 10, 14, 32, 1, tzinfo=timezone.utc)


@pytest.fixture
def sample_vehicle_id() -> str:
    """Provide a sample vehicle ID."""
    return "AMB-001"


@pytest.fixture
def sample_geolocation_data() -> dict:
    """Provide sample geolocation data."""
    return {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "altitude": 15.5,
        "accuracy": 5.0,
        "heading": 45.0,
        "speed_kmh": 65.5,
        "timestamp": datetime(2026, 2, 10, 14, 32, 1, tzinfo=timezone.utc),
    }


@pytest.fixture
def sample_vehicle_identity_data() -> dict:
    """Provide sample vehicle identity data."""
    return {
        "vehicle_id": "AMB-001",
        "vehicle_type": VehicleType.AMBULANCE,
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


@pytest.fixture
def sample_vehicle_state_data(sample_datetime: datetime) -> dict:
    """Provide sample vehicle state data."""
    return {
        "vehicle_id": "AMB-001",
        "timestamp": sample_datetime,
        "operational_status": OperationalStatus.EN_ROUTE,
        "mission_id": "MISSION-2026-02-10-001",
        "crew_count": 3,
        "assigned_crew": ["crew_001", "crew_002", "crew_003"],
        "eta_seconds": 420,
    }


@pytest.fixture
def sample_telemetry_data(sample_datetime: datetime, sample_geolocation_data: dict) -> dict:
    """Provide sample telemetry data."""
    return {
        "vehicle_id": "AMB-001",
        "timestamp": sample_datetime,
        "sequence_number": 12345,
        "location": sample_geolocation_data,
        "odometer_km": 45678.9,
        "engine_temp_celsius": 92.5,
        "engine_rpm": 2500,
        "coolant_temp_celsius": 90.0,
        "oil_pressure_psi": 45.0,
        "oil_temp_celsius": 95.0,
        "transmission_temp_celsius": 85.0,
        "throttle_position_percent": 60.0,
        "battery_voltage": 13.8,
        "battery_current_amps": 5.0,
        "alternator_voltage": 14.2,
        "battery_state_of_charge_percent": 95.0,
        "battery_health_percent": 98.0,
        "fuel_level_percent": 75.0,
        "fuel_level_liters": 30.0,
        "fuel_consumption_lph": 12.5,
        "fuel_economy_kml": 8.5,
        "brake_pad_thickness_mm": {
            "front_left": 10.0,
            "front_right": 10.0,
            "rear_left": 10.0,
            "rear_right": 10.0,
        },
        "brake_fluid_level_percent": 95.0,
        "brake_temp_celsius": {
            "front_left": 150.0,
            "front_right": 150.0,
            "rear_left": 120.0,
            "rear_right": 120.0,
        },
        "abs_active": False,
        "tire_pressure_psi": {
            "front_left": 80.0,
            "front_right": 80.0,
            "rear_left": 80.0,
            "rear_right": 80.0,
        },
        "tire_temp_celsius": {
            "front_left": 45.0,
            "front_right": 45.0,
            "rear_left": 40.0,
            "rear_right": 40.0,
        },
        "suspension_travel_mm": {
            "front_left": 50.0,
            "front_right": 50.0,
            "rear_left": 55.0,
            "rear_right": 55.0,
        },
        "vibration_g_force": {"x": 0.05, "y": 0.03, "z": 0.98},
        "cabin_temp_celsius": 22.0,
        "exterior_temp_celsius": 20.0,
        "humidity_percent": 55.0,
        "siren_active": True,
        "lights_active": True,
        "equipment_status": {},
        "active_dtc_codes": [],
    }


@pytest.fixture
def sample_predictive_alert_data(sample_datetime: datetime) -> dict:
    """Provide sample predictive alert data."""
    return {
        "vehicle_id": "AMB-001",
        "timestamp": sample_datetime,
        "severity": AlertSeverity.WARNING,
        "category": FailureCategory.ELECTRICAL,
        "component": "alternator",
        "failure_probability": 0.75,
        "confidence": 0.88,
        "predicted_failure_min_hours": 8.0,
        "predicted_failure_max_hours": 24.0,
        "predicted_failure_likely_hours": 12.0,
        "can_complete_current_mission": True,
        "safe_to_operate": True,
        "recommended_action": "Schedule alternator inspection within 12 hours",
        "contributing_factors": [
            "battery_voltage declining trend",
            "alternator_voltage below 13.5V",
            "increased electrical load",
        ],
        "related_telemetry": {
            "battery_voltage": 12.8,
            "alternator_voltage": 13.2,
        },
        "model_version": "1.0.0",
    }


@pytest.fixture
def sample_maintenance_recommendation_data(sample_datetime: datetime) -> dict:
    """Provide sample maintenance recommendation data."""
    return {
        "vehicle_id": "AMB-001",
        "timestamp": sample_datetime,
        "urgency": MaintenanceUrgency.URGENT,
        "component": "alternator",
        "issue_description": "Alternator output voltage declining, bearing wear detected",
        "recommended_action": "Replace alternator assembly",
        "estimated_downtime_hours": 2.5,
        "parts_needed": ["Alternator Assembly 14V 200A", "Serpentine Belt"],
        "estimated_labor_hours": 2.0,
        "estimated_cost_usd": 450.00,
        "can_defer": True,
        "deferral_risk": "Risk of complete electrical failure within 24 hours",
    }


@pytest.fixture
def sample_message_data(sample_datetime: datetime) -> dict:
    """Provide sample message envelope data."""
    return {
        "message_type": MessageType.TELEMETRY_UPDATE,
        "timestamp": sample_datetime,
        "source": "AMB-001",
        "destination": "orchestrator",
        "priority": MessagePriority.NORMAL,
        "payload": {"test": "data"},
        "ttl_seconds": 60,
    }


@pytest.fixture
def sample_heartbeat_payload_data() -> dict:
    """Provide sample heartbeat payload data."""
    return {
        "vehicle_id": "AMB-001",
        "uptime_seconds": 86400,
        "last_telemetry_sequence": 12345,
        "agent_version": "1.0.0",
        "system_health": {
            "cpu_percent": 15.5,
            "memory_percent": 42.3,
            "disk_percent": 58.1,
            "network_latency_ms": 12.5,
            "redis_connected": True,
        },
    }


@pytest.fixture
def sample_command_payload_data() -> dict:
    """Provide sample command payload data."""
    return {
        "command_type": CommandType.DISPATCH,
        "parameters": {
            "mission_id": "MISSION-2026-02-10-001",
            "destination": {
                "latitude": 37.8049,
                "longitude": -122.4194,
                "address": "123 Emergency St, San Francisco, CA",
            },
            "priority": "life_threatening",
        },
        "reason": "Cardiac arrest reported",
        "issued_by": "dispatcher_user_42",
        "requires_acknowledgment": True,
    }


@pytest.fixture
def sample_scenario_parameters_data() -> dict:
    """Provide sample scenario parameters data."""
    return {
        "scenario": FailureScenario.ENGINE_OVERHEAT,
        "trigger_after_seconds": 300,
        "progression_rate": 0.5,
        "baseline_probability": 0.2,
        "affected_metrics": [
            "engine_temp_celsius",
            "coolant_temp_celsius",
            "engine_rpm",
        ],
        "noise_level": 0.15,
    }


@pytest.fixture
def sample_simulation_config_data() -> dict:
    """Provide sample simulation configuration data."""
    return {
        "simulation_id": "sim-2026-02-10-001",
        "duration_seconds": 3600,
        "num_vehicles": 10,
        "vehicle_types": {
            VehicleType.AMBULANCE: 6,
            VehicleType.FIRE_TRUCK: 4,
        },
        "inject_failures": True,
        "failure_scenarios": [
            FailureScenario.ENGINE_OVERHEAT,
            FailureScenario.ALTERNATOR_FAILURE,
            FailureScenario.BATTERY_DEGRADATION,
        ],
        "random_failure_probability": 0.05,
        "telemetry_frequency_hz": 1.0,
        "add_realistic_noise": True,
        "simulate_gps_drift": True,
        "dispatch_probability_per_hour": 2.0,
        "mission_duration_avg_minutes": 30,
        "weather_conditions": "clear",
        "time_of_day": "day",
    }


@pytest.fixture
def sample_weather_conditions_data() -> dict:
    """Provide sample weather conditions data."""
    return {
        "condition_type": "clear",
        "ambient_temp_celsius": 20.0,
        "humidity_percent": 50.0,
        "road_friction": 1.0,
        "visibility_factor": 1.0,
    }
