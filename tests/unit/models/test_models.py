import pytest
from datetime import datetime

from src.models import (
    AlertSeverity,
    FailureCategory,
    FailureScenario,
    Location,
    OperationalStatus,
    PredictiveAlert,
    Vehicle,
    VehicleTelemetry,
    VehicleType,
)


def test_vehicle_creation():
    """Test creating a Vehicle model."""
    vehicle = Vehicle(
        vehicle_id="AMB-001",
        vehicle_type=VehicleType.AMBULANCE,
        operational_status=OperationalStatus.EN_ROUTE,
        location=Location(latitude=37.7749, longitude=-122.4194),
    )

    assert vehicle.vehicle_id == "AMB-001"
    assert vehicle.vehicle_type == VehicleType.AMBULANCE
    assert vehicle.operational_status == OperationalStatus.EN_ROUTE
    assert vehicle.location.latitude == 37.7749
    assert vehicle.location.longitude == -122.4194


def test_telemetry_creation():
    """Test creating a VehicleTelemetry model."""
    now = datetime.utcnow()
    telemetry = VehicleTelemetry(
        vehicle_id="AMB-001",
        timestamp=now,
        latitude=37.7749,
        longitude=-122.4194,
        speed_kmh=65.5,
        engine_temp_celsius=92.5,
        battery_voltage=13.8,
        fuel_level_percent=75.0,
    )

    assert telemetry.vehicle_id == "AMB-001"
    assert telemetry.timestamp == now
    assert telemetry.latitude == 37.7749
    assert telemetry.longitude == -122.4194
    assert telemetry.speed_kmh == 65.5
    assert telemetry.engine_temp_celsius == 92.5
    assert telemetry.battery_voltage == 13.8
    assert telemetry.fuel_level_percent == 75.0


def test_predictive_alert_creation():
    """Test creating a PredictiveAlert model."""
    now = datetime.utcnow()
    alert = PredictiveAlert(
        vehicle_id="AMB-001",
        timestamp=now,
        severity=AlertSeverity.WARNING,
        category=FailureCategory.ENGINE,
        component="engine_temp",
        failure_probability=0.85,
        recommended_action="Schedule immediate engine inspection",
    )

    assert alert.alert_id is not None
    assert alert.vehicle_id == "AMB-001"
    assert alert.timestamp == now
    assert alert.severity == AlertSeverity.WARNING
    assert alert.category == FailureCategory.ENGINE
    assert alert.component == "engine_temp"
    assert alert.failure_probability == 0.85
    assert alert.recommended_action == "Schedule immediate engine inspection"
    assert alert.acknowledged is False
