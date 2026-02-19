"""Unit tests for failure injector."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from src.models.enums import FailureScenario, VehicleType
from src.models.telemetry import VehicleTelemetry
from src.models.vehicle import GeoLocation
from src.vehicle_agent.failure_injector import FailureInjector


class TestFailureInjector:
    """Test suite for FailureInjector."""

    @pytest.fixture
    def injector(self) -> FailureInjector:
        """Create a failure injector."""
        return FailureInjector()

    @pytest.fixture
    def sample_telemetry(self) -> VehicleTelemetry:
        """Create sample telemetry for testing."""
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
        )

    def test_injector_initialization(self, injector: FailureInjector) -> None:
        """Test injector initializes with no active scenarios."""
        assert len(injector.active_scenarios) == 0

    def test_activate_scenario(self, injector: FailureInjector) -> None:
        """Test activating a failure scenario."""
        injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

        assert FailureScenario.ENGINE_OVERHEAT in injector.active_scenarios
        assert isinstance(injector.active_scenarios[FailureScenario.ENGINE_OVERHEAT], datetime)

    def test_deactivate_scenario(self, injector: FailureInjector) -> None:
        """Test deactivating a failure scenario."""
        injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)
        injector.deactivate_scenario(FailureScenario.ENGINE_OVERHEAT)

        assert FailureScenario.ENGINE_OVERHEAT not in injector.active_scenarios

    def test_get_time_since_activation_not_active(self, injector: FailureInjector) -> None:
        """Test getting time for inactive scenario returns 0."""
        elapsed = injector.get_time_since_activation(FailureScenario.ENGINE_OVERHEAT)
        assert elapsed == 0.0

    def test_get_time_since_activation_active(self, injector: FailureInjector) -> None:
        """Test getting time for active scenario."""
        # Mock datetime to control time
        fake_start = datetime(2026, 2, 10, 12, 0, 0)
        fake_now = datetime(2026, 2, 10, 12, 0, 30)  # 30 seconds later

        with patch("src.vehicle_agent.failure_injector.datetime") as mock_dt:
            mock_dt.utcnow.return_value = fake_start
            injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

            mock_dt.utcnow.return_value = fake_now
            elapsed = injector.get_time_since_activation(FailureScenario.ENGINE_OVERHEAT)

        assert elapsed == 30.0

    def test_apply_failures_no_active_scenarios(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test applying failures with no active scenarios returns unchanged telemetry."""
        result = injector.apply_failures(sample_telemetry)

        # Telemetry should be unchanged
        assert result.engine_temp_celsius == sample_telemetry.engine_temp_celsius
        assert (
            result.battery_state_of_charge_percent
            == sample_telemetry.battery_state_of_charge_percent
        )

    def test_apply_engine_overheat_initial(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine overheat scenario at initialization (0 minutes)."""
        injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

        # Immediately after activation (0 minutes elapsed)
        result = injector.apply_failures(sample_telemetry)

        # Temperature should be at baseline (no increase yet)
        assert result.engine_temp_celsius == pytest.approx(90.0, abs=0.1)
        assert result.coolant_temp_celsius == pytest.approx(85.0, abs=0.1)

    def test_apply_engine_overheat_progression(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test engine overheat progresses over time."""
        fake_start = datetime(2026, 2, 10, 12, 0, 0)
        fake_15min = datetime(2026, 2, 10, 12, 15, 0)  # 15 minutes later

        with patch("src.vehicle_agent.failure_injector.datetime") as mock_dt:
            mock_dt.utcnow.return_value = fake_start
            injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

            # Check after 15 minutes (should be at WARNING threshold)
            mock_dt.utcnow.return_value = fake_15min
            result = injector.apply_failures(sample_telemetry)

        # After 15 min: +2°C/min * 15 = +30°C -> 120°C total
        assert result.engine_temp_celsius == pytest.approx(120.0, abs=0.1)
        # Coolant: +2.5°C/min * 15 = +37.5°C -> 122.5°C
        assert result.coolant_temp_celsius == pytest.approx(122.5, abs=0.1)

    def test_apply_alternator_failure_initial(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test alternator failure at initialization."""
        injector.activate_scenario(FailureScenario.ALTERNATOR_FAILURE)

        result = injector.apply_failures(sample_telemetry)

        # Voltage should be at baseline initially
        assert result.alternator_voltage == pytest.approx(14.2, abs=0.1)
        assert result.battery_state_of_charge_percent == pytest.approx(100.0, abs=1.0)

    def test_apply_alternator_failure_progression(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test alternator failure progresses over time."""
        fake_start = datetime(2026, 2, 10, 12, 0, 0)
        fake_40min = datetime(2026, 2, 10, 12, 40, 0)  # 40 minutes later

        with patch("src.vehicle_agent.failure_injector.datetime") as mock_dt:
            mock_dt.utcnow.return_value = fake_start
            injector.activate_scenario(FailureScenario.ALTERNATOR_FAILURE)

            mock_dt.utcnow.return_value = fake_40min
            result = injector.apply_failures(sample_telemetry)

        # After 40 min: -0.1V per 5min -> -0.8V total = 13.4V (WARNING range)
        assert result.alternator_voltage == pytest.approx(13.4, abs=0.1)
        # Battery: -3% per min * 40 = -120%, clamped to 0%
        assert result.battery_state_of_charge_percent == 0.0
        # Battery voltage correlates with SOC (0% -> 11.5V)
        assert result.battery_voltage == pytest.approx(11.5, abs=0.1)

    def test_apply_brake_pad_wear_initial(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test brake pad wear at initialization."""
        injector.activate_scenario(FailureScenario.BRAKE_PAD_WEAR_CRITICAL)

        result = injector.apply_failures(sample_telemetry)

        # Pads should be at initial thickness
        assert result.brake_pad_thickness_mm["front_left"] == pytest.approx(8.0, abs=0.1)
        assert result.brake_pad_thickness_mm["rear_left"] == pytest.approx(9.0, abs=0.1)

    def test_apply_brake_pad_wear_progression(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test brake pad wear progresses over time."""
        fake_start = datetime(2026, 2, 10, 12, 0, 0)
        fake_100min = datetime(2026, 2, 10, 13, 40, 0)  # 100 minutes later

        with patch("src.vehicle_agent.failure_injector.datetime") as mock_dt:
            mock_dt.utcnow.return_value = fake_start
            injector.activate_scenario(FailureScenario.BRAKE_PAD_WEAR_CRITICAL)

            mock_dt.utcnow.return_value = fake_100min
            result = injector.apply_failures(sample_telemetry)

        # After 100 min: 0.05mm/min * 100 = 5.0mm wear
        # Front wears 30% faster: 5.0 * 1.3 = 6.5mm -> 8.0 - 6.5 = 1.5mm (CRITICAL)
        assert result.brake_pad_thickness_mm["front_left"] == pytest.approx(1.5, abs=0.1)
        # Rear: 8.0 - 5.0 = 4.0mm (WARNING range)
        assert result.brake_pad_thickness_mm["rear_left"] == pytest.approx(4.0, abs=0.1)

    def test_apply_tire_leak_initial(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test tire leak at initialization."""
        injector.activate_scenario(FailureScenario.TIRE_PRESSURE_LOW)

        result = injector.apply_failures(sample_telemetry)

        # Pressure should be at baseline
        assert result.tire_pressure_psi["front_left"] == pytest.approx(80.0, abs=0.1)

    def test_apply_tire_leak_progression(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test tire leak progresses over time."""
        fake_start = datetime(2026, 2, 10, 12, 0, 0)
        fake_10min = datetime(2026, 2, 10, 12, 10, 0)  # 10 minutes later

        with patch("src.vehicle_agent.failure_injector.datetime") as mock_dt:
            mock_dt.utcnow.return_value = fake_start
            injector.activate_scenario(FailureScenario.TIRE_PRESSURE_LOW)

            mock_dt.utcnow.return_value = fake_10min
            result = injector.apply_failures(sample_telemetry)

        # After 10 min: -2 psi/min * 10 = -20 psi -> 60 psi (WARNING threshold)
        assert result.tire_pressure_psi["front_left"] == pytest.approx(60.0, abs=0.1)
        # Vibration should increase
        assert result.vibration_g_force["z"] > sample_telemetry.vibration_g_force.get("z", 0.0)

    def test_apply_multiple_failures(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test applying multiple failure scenarios simultaneously."""
        fake_start = datetime(2026, 2, 10, 12, 0, 0)
        fake_10min = datetime(2026, 2, 10, 12, 10, 0)  # 10 minutes later

        with patch("src.vehicle_agent.failure_injector.datetime") as mock_dt:
            # Activate both scenarios at the same time
            mock_dt.utcnow.return_value = fake_start
            injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)
            injector.activate_scenario(FailureScenario.ALTERNATOR_FAILURE)

            # Check after 10 minutes
            mock_dt.utcnow.return_value = fake_10min
            result = injector.apply_failures(sample_telemetry)

        # Both failures should be applied
        # Engine overheat effect: +2°C/min * 10 = +20°C -> 110°C
        assert result.engine_temp_celsius == pytest.approx(110.0, abs=0.1)
        # Alternator failure effect: -0.1V per 5min * 2 = -0.2V -> 14.0V
        assert result.alternator_voltage == pytest.approx(14.0, abs=0.1)

    def test_telemetry_immutability(
        self, injector: FailureInjector, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test that original telemetry is not modified."""
        injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

        original_temp = sample_telemetry.engine_temp_celsius
        result = injector.apply_failures(sample_telemetry)

        # Original should be unchanged
        assert sample_telemetry.engine_temp_celsius == original_temp
        # Result should be different
        assert result.engine_temp_celsius != original_temp
