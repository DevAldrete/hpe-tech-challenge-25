"""Unit tests for anomaly detector."""

from datetime import datetime

import pytest

from src.models.enums import AlertSeverity, FailureCategory
from src.models.telemetry import VehicleTelemetry
from src.models.vehicle import GeoLocation
from src.vehicle_agent.anomaly_detector import AnomalyDetector


class TestAnomalyDetector:
    """Test suite for AnomalyDetector."""

    @pytest.fixture
    def detector(self) -> AnomalyDetector:
        """Create an anomaly detector."""
        return AnomalyDetector(vehicle_id="AMB-001")

    @pytest.fixture
    def normal_telemetry(self) -> VehicleTelemetry:
        """Create normal telemetry with no anomalies."""
        return VehicleTelemetry(
            vehicle_id="AMB-001",
            timestamp=datetime.utcnow(),
            sequence_number=1,
            location=GeoLocation(
                latitude=37.7749,
                longitude=-122.4194,
                speed_kmh=65.0,
                heading=45.0,
                timestamp=datetime.utcnow(),
            ),
            odometer_km=50000.0,
            engine_temp_celsius=90.0,
            engine_rpm=2000,
            coolant_temp_celsius=85.0,
            oil_pressure_psi=45.0,
            oil_temp_celsius=90.0,
            transmission_temp_celsius=80.0,
            throttle_position_percent=30.0,
            battery_voltage=13.8,
            battery_current_amps=10.0,
            alternator_voltage=14.2,
            battery_state_of_charge_percent=100.0,
            battery_health_percent=95.0,
            fuel_level_percent=75.0,
            fuel_level_liters=30.0,
            brake_fluid_level_percent=100.0,
            brake_pad_thickness_mm={
                "front_left": 8.0,
                "front_right": 8.0,
                "rear_left": 8.0,
                "rear_right": 8.0,
            },
            tire_pressure_psi={
                "front_left": 80.0,
                "front_right": 80.0,
                "rear_left": 80.0,
                "rear_right": 80.0,
            },
        )

    def test_detector_initialization(self, detector: AnomalyDetector) -> None:
        """Test detector initializes with vehicle ID."""
        assert detector.vehicle_id == "AMB-001"

    def test_analyze_normal_telemetry_no_alerts(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test normal telemetry generates no alerts."""
        alerts = detector.analyze(normal_telemetry)
        assert len(alerts) == 0

    # Engine Temperature Tests
    def test_engine_temp_below_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine temp at 104°C (just below 105°C warning) generates no alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.engine_temp_celsius = 104.0

        alerts = detector._check_engine_temp(telemetry)
        assert len(alerts) == 0

    def test_engine_temp_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine temp at 106°C generates WARNING alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.engine_temp_celsius = 106.0

        alerts = detector._check_engine_temp(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].category == FailureCategory.ENGINE
        assert alerts[0].component == "engine"
        assert alerts[0].can_complete_current_mission is True
        assert alerts[0].safe_to_operate is True
        assert "106.0" in alerts[0].contributing_factors[0]

    def test_engine_temp_critical_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine temp at 121°C generates CRITICAL alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.engine_temp_celsius = 121.0

        alerts = detector._check_engine_temp(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].category == FailureCategory.ENGINE
        assert alerts[0].can_complete_current_mission is False
        assert alerts[0].safe_to_operate is False
        assert "STOP IMMEDIATELY" in alerts[0].recommended_action

    # Alternator Tests
    def test_alternator_voltage_normal(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test alternator at 14.0V (normal) generates no alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.alternator_voltage = 14.0

        alerts = detector._check_alternator(telemetry)
        assert len(alerts) == 0

    def test_alternator_voltage_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test alternator at 13.4V generates WARNING alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.alternator_voltage = 13.4

        alerts = detector._check_alternator(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].category == FailureCategory.ELECTRICAL
        assert alerts[0].component == "alternator"
        assert alerts[0].can_complete_current_mission is True

    def test_alternator_voltage_critical_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test alternator at 12.9V generates CRITICAL alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.alternator_voltage = 12.9

        alerts = detector._check_alternator(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].category == FailureCategory.ELECTRICAL
        assert "Replace alternator" in alerts[0].recommended_action

    # Battery Tests
    def test_battery_soc_normal(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test battery at 50% (normal) generates no alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.battery_state_of_charge_percent = 50.0

        alerts = detector._check_battery(telemetry)
        assert len(alerts) == 0

    def test_battery_soc_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test battery at 35% generates WARNING alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.battery_state_of_charge_percent = 35.0

        alerts = detector._check_battery(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].category == FailureCategory.ELECTRICAL
        assert alerts[0].component == "battery"

    def test_battery_soc_critical_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test battery at 15% generates CRITICAL alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.battery_state_of_charge_percent = 15.0

        alerts = detector._check_battery(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].can_complete_current_mission is False
        assert alerts[0].safe_to_operate is False

    # Brake Pad Tests
    def test_brake_pads_normal(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test brake pads at 8mm (normal) generate no alerts."""
        # Already set to 8mm in fixture
        alerts = detector._check_brake_pads(normal_telemetry)
        assert len(alerts) == 0

    def test_brake_pad_warning_single_wheel(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test single brake pad at 2.5mm generates WARNING alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.brake_pad_thickness_mm["front_left"] = 2.5

        alerts = detector._check_brake_pads(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].category == FailureCategory.BRAKES
        assert alerts[0].component == "brake_pad_front_left"
        assert "front_left" in alerts[0].recommended_action

    def test_brake_pad_critical_single_wheel(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test single brake pad at 1.2mm generates CRITICAL alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.brake_pad_thickness_mm["rear_right"] = 1.2

        alerts = detector._check_brake_pads(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].component == "brake_pad_rear_right"
        assert alerts[0].can_complete_current_mission is False
        assert "metal-on-metal" in alerts[0].recommended_action

    def test_brake_pads_multiple_warnings(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test multiple brake pads below threshold generate multiple alerts."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.brake_pad_thickness_mm["front_left"] = 2.5
        telemetry.brake_pad_thickness_mm["front_right"] = 1.2

        alerts = detector._check_brake_pads(telemetry)
        assert len(alerts) == 2
        # One WARNING, one CRITICAL
        severities = {alert.severity for alert in alerts}
        assert AlertSeverity.WARNING in severities
        assert AlertSeverity.CRITICAL in severities

    # Tire Pressure Tests
    def test_tire_pressure_normal(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test tire pressure at 80 psi (normal) generates no alerts."""
        # Already set to 80 psi in fixture
        alerts = detector._check_tire_pressure(normal_telemetry)
        assert len(alerts) == 0

    def test_tire_pressure_warning_single_tire(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test single tire at 55 psi generates WARNING alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.tire_pressure_psi["front_left"] = 55.0

        alerts = detector._check_tire_pressure(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.WARNING
        assert alerts[0].category == FailureCategory.TIRES
        assert alerts[0].component == "tire_front_left"
        assert "front_left" in alerts[0].recommended_action

    def test_tire_pressure_critical_single_tire(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test single tire at 35 psi generates CRITICAL alert."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.tire_pressure_psi["rear_left"] = 35.0

        alerts = detector._check_tire_pressure(telemetry)
        assert len(alerts) == 1
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert alerts[0].component == "tire_rear_left"
        assert alerts[0].can_complete_current_mission is False
        assert "Stop and replace" in alerts[0].recommended_action

    def test_tire_pressure_multiple_warnings(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test multiple tires below threshold generate multiple alerts."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.tire_pressure_psi["front_left"] = 55.0
        telemetry.tire_pressure_psi["rear_right"] = 38.0

        alerts = detector._check_tire_pressure(telemetry)
        assert len(alerts) == 2
        severities = {alert.severity for alert in alerts}
        assert AlertSeverity.WARNING in severities
        assert AlertSeverity.CRITICAL in severities

    # Integration Tests
    def test_analyze_multiple_simultaneous_anomalies(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test analyze detects multiple simultaneous failures."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.engine_temp_celsius = 121.0  # CRITICAL
        telemetry.alternator_voltage = 12.9  # CRITICAL
        telemetry.battery_state_of_charge_percent = 15.0  # CRITICAL
        telemetry.brake_pad_thickness_mm["front_left"] = 1.2  # CRITICAL
        telemetry.tire_pressure_psi["rear_right"] = 38.0  # CRITICAL

        alerts = detector.analyze(telemetry)
        # Should generate 5 CRITICAL alerts
        assert len(alerts) == 5
        assert all(alert.severity == AlertSeverity.CRITICAL for alert in alerts)

        # Check all categories are represented
        categories = {alert.category for alert in alerts}
        assert FailureCategory.ENGINE in categories
        assert FailureCategory.ELECTRICAL in categories
        assert FailureCategory.BRAKES in categories
        assert FailureCategory.TIRES in categories

    def test_analyze_mixed_severity_alerts(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test analyze detects mixed WARNING and CRITICAL alerts."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.engine_temp_celsius = 106.0  # WARNING
        telemetry.alternator_voltage = 12.9  # CRITICAL
        telemetry.battery_state_of_charge_percent = 35.0  # WARNING

        alerts = detector.analyze(telemetry)
        assert len(alerts) == 3

        warnings = [a for a in alerts if a.severity == AlertSeverity.WARNING]
        criticals = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]

        assert len(warnings) == 2
        assert len(criticals) == 1

    def test_alert_metadata_completeness(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test alerts contain all required metadata fields."""
        telemetry = normal_telemetry.model_copy(deep=True)
        telemetry.engine_temp_celsius = 121.0

        alerts = detector.analyze(telemetry)
        assert len(alerts) == 1
        alert = alerts[0]

        # Verify all key fields are populated
        assert alert.vehicle_id == "AMB-001"
        assert alert.timestamp is not None
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.category == FailureCategory.ENGINE
        assert alert.component == "engine"
        assert 0.0 <= alert.failure_probability <= 1.0
        assert 0.0 <= alert.confidence <= 1.0
        assert alert.predicted_failure_min_hours is not None
        assert alert.predicted_failure_max_hours is not None
        assert alert.predicted_failure_likely_hours is not None
        assert alert.can_complete_current_mission is not None
        assert alert.safe_to_operate is not None
        assert alert.recommended_action != ""
        assert len(alert.contributing_factors) > 0
        assert len(alert.related_telemetry) > 0
