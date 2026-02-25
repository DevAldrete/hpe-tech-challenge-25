"""Unit tests for anomaly detection."""

from datetime import UTC, datetime

import pytest

from src.models.enums import AlertSeverity, FailureCategory
from src.models.telemetry import VehicleTelemetry
from src.vehicle_agent.anomaly_detector import AnomalyDetector


class TestAnomalyDetector:
    """Test suite for AnomalyDetector."""

    @pytest.fixture
    def detector(self) -> AnomalyDetector:
        """Create anomaly detector instance."""
        return AnomalyDetector("AMB-001")

    @pytest.fixture
    def normal_telemetry(self) -> VehicleTelemetry:
        """Create normal telemetry with no anomalies."""
        return VehicleTelemetry(
            vehicle_id="AMB-001",
            timestamp=datetime.now(UTC),
            latitude=37.7749,
            longitude=-122.4194,
            speed_kmh=0.0,
            odometer_km=1000.0,
            engine_temp_celsius=90.0,
            battery_voltage=13.8,
            fuel_level_percent=75.0,
        )

    def test_detector_initialization(self, detector: AnomalyDetector) -> None:
        """Test detector initializes correctly."""
        assert detector.vehicle_id == "AMB-001"

    def test_analyze_normal_telemetry_no_alerts(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test normal telemetry generates no alerts."""
        alerts = detector.analyze(normal_telemetry)
        assert len(alerts) == 0

    def test_engine_temp_below_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine temp below threshold generates no alerts."""
        normal_telemetry.engine_temp_celsius = 104.9
        alerts = detector.analyze(normal_telemetry)
        assert len(alerts) == 0

    def test_engine_temp_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine temp warning threshold."""
        normal_telemetry.engine_temp_celsius = 106.0
        alerts = detector.analyze(normal_telemetry)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.component == "engine"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.category == FailureCategory.ENGINE

    def test_engine_temp_critical_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine temp critical threshold."""
        normal_telemetry.engine_temp_celsius = 125.0
        alerts = detector.analyze(normal_telemetry)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.component == "engine"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.category == FailureCategory.ENGINE
        assert alert.safe_to_operate is False

    def test_battery_voltage_normal(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test normal battery generates no alerts."""
        normal_telemetry.battery_voltage = 12.5
        alerts = detector.analyze(normal_telemetry)
        assert len(alerts) == 0

    def test_battery_voltage_warning_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test battery warning threshold."""
        normal_telemetry.battery_voltage = 11.8
        alerts = detector.analyze(normal_telemetry)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.component == "battery"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.category == FailureCategory.ELECTRICAL

    def test_battery_voltage_critical_threshold(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test battery critical threshold."""
        normal_telemetry.battery_voltage = 11.2
        alerts = detector.analyze(normal_telemetry)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.component == "battery"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.category == FailureCategory.ELECTRICAL

    def test_fuel_level_warning(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test low fuel warning."""
        normal_telemetry.fuel_level_percent = 14.0
        alerts = detector.analyze(normal_telemetry)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.component == "fuel"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.category == FailureCategory.FUEL

    def test_fuel_level_critical(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test critical fuel level."""
        normal_telemetry.fuel_level_percent = 4.0
        alerts = detector.analyze(normal_telemetry)

        assert len(alerts) == 1
        alert = alerts[0]
        assert alert.component == "fuel"
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.category == FailureCategory.FUEL

    def test_analyze_multiple_simultaneous_anomalies(
        self, detector: AnomalyDetector, normal_telemetry: VehicleTelemetry
    ) -> None:
        """Test multiple simultaneous anomalies."""
        normal_telemetry.engine_temp_celsius = 106.0
        normal_telemetry.battery_voltage = 11.2
        normal_telemetry.fuel_level_percent = 4.0

        alerts = detector.analyze(normal_telemetry)
        assert len(alerts) == 3

        components = {alert.component for alert in alerts}
        assert "engine" in components
        assert "battery" in components
        assert "fuel" in components
