"""Unit tests for telemetry generator."""

import pytest

from src.models.enums import VehicleType
from src.vehicle_agent.config import AgentConfig
from src.vehicle_agent.telemetry_generator import SimpleTelemetryGenerator


class TestSimpleTelemetryGenerator:
    """Test suite for SimpleTelemetryGenerator."""

    @pytest.fixture
    def config(self) -> AgentConfig:
        """Create a test configuration."""
        return AgentConfig(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
        )

    @pytest.fixture
    def generator(self, config: AgentConfig) -> SimpleTelemetryGenerator:
        """Create a telemetry generator."""
        return SimpleTelemetryGenerator(config)

    def test_generator_initialization(self, generator: SimpleTelemetryGenerator) -> None:
        """Test generator initializes correctly."""
        assert generator.sequence_number == 0
        assert "engine_temp_celsius" in generator.baselines
        assert "battery_voltage" in generator.baselines

    def test_generate_telemetry(self, generator: SimpleTelemetryGenerator) -> None:
        """Test generating telemetry data."""
        telemetry = generator.generate()

        assert telemetry.vehicle_id == "AMB-001"
        assert telemetry.sequence_number == 1
        assert telemetry.timestamp is not None

    def test_sequence_number_increments(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that sequence number increments with each generation."""
        telemetry1 = generator.generate()
        telemetry2 = generator.generate()
        telemetry3 = generator.generate()

        assert telemetry1.sequence_number == 1
        assert telemetry2.sequence_number == 2
        assert telemetry3.sequence_number == 3

    def test_telemetry_values_in_valid_range(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that generated values are within valid ranges."""
        telemetry = generator.generate()

        # Engine temperature should be around 90°C ± some noise
        assert 80.0 <= telemetry.engine_temp_celsius <= 100.0

        # Battery voltage should be around 13.8V ± some noise
        assert 12.0 <= telemetry.battery_voltage <= 15.0

        # Fuel level should be around 75% ± some noise
        assert 70.0 <= telemetry.fuel_level_percent <= 80.0

        # Tire pressure should be around 80 psi ± some noise
        for wheel, pressure in telemetry.tire_pressure_psi.items():
            assert 75.0 <= pressure <= 85.0

    def test_telemetry_location_matches_config(
        self, config: AgentConfig, generator: SimpleTelemetryGenerator
    ) -> None:
        """Test that location matches initial configuration."""
        telemetry = generator.generate()

        assert telemetry.location.latitude == config.initial_latitude
        assert telemetry.location.longitude == config.initial_longitude
        assert telemetry.location.altitude == config.initial_altitude
        assert telemetry.location.speed_kmh == 0.0  # Parked

    def test_telemetry_idle_characteristics(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that telemetry reflects idle vehicle characteristics."""
        telemetry = generator.generate()

        # Should be at idle RPM
        assert 700 <= telemetry.engine_rpm <= 900

        # Should not be moving
        assert telemetry.location.speed_kmh == 0.0
        assert telemetry.throttle_position_percent == 0.0

        # Emergency equipment should be off
        assert telemetry.siren_active is False
        assert telemetry.lights_active is False
        assert telemetry.abs_active is False

        # Should have no active DTCs
        assert len(telemetry.active_dtc_codes) == 0

    def test_add_noise_variability(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that noise produces different values."""
        values = []
        for _ in range(10):
            telemetry = generator.generate()
            values.append(telemetry.engine_temp_celsius)

        # All values should be different (extremely unlikely to be identical with noise)
        assert len(set(values)) > 1

    def test_telemetry_has_all_required_fields(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that telemetry has all required fields."""
        telemetry = generator.generate()

        # Required fields
        assert telemetry.vehicle_id is not None
        assert telemetry.timestamp is not None
        assert telemetry.sequence_number > 0
        assert telemetry.location is not None

        # Engine metrics
        assert telemetry.engine_temp_celsius is not None
        assert telemetry.engine_rpm is not None
        assert telemetry.oil_pressure_psi is not None

        # Electrical metrics
        assert telemetry.battery_voltage is not None
        assert telemetry.alternator_voltage is not None

        # Fuel metrics
        assert telemetry.fuel_level_percent is not None
        assert telemetry.fuel_level_liters is not None

        # Tire metrics
        assert len(telemetry.tire_pressure_psi) == 4
        assert "front_left" in telemetry.tire_pressure_psi
        assert "front_right" in telemetry.tire_pressure_psi
        assert "rear_left" in telemetry.tire_pressure_psi
        assert "rear_right" in telemetry.tire_pressure_psi

    def test_brake_pad_thickness_initialized(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that brake pad thickness is properly initialized."""
        telemetry = generator.generate()

        assert len(telemetry.brake_pad_thickness_mm) == 4
        assert telemetry.brake_pad_thickness_mm["front_left"] == 8.0
        assert telemetry.brake_pad_thickness_mm["front_right"] == 8.0
        assert telemetry.brake_pad_thickness_mm["rear_left"] == 9.0
        assert telemetry.brake_pad_thickness_mm["rear_right"] == 9.0
