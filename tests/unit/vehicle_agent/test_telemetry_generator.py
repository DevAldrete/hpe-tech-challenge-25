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
        assert "engine_temp_celsius" in generator.baselines
        assert "battery_voltage" in generator.baselines

    def test_generate_telemetry(self, generator: SimpleTelemetryGenerator) -> None:
        """Test generating telemetry data."""
        telemetry = generator.generate()

        assert telemetry.vehicle_id == "AMB-001"
        assert telemetry.timestamp is not None

    def test_telemetry_values_in_valid_range(self, generator: SimpleTelemetryGenerator) -> None:
        """Test that generated values are within valid ranges."""
        telemetry = generator.generate()

        # Engine temperature should be around 90°C ± some noise
        assert 80.0 <= telemetry.engine_temp_celsius <= 100.0

        # Battery voltage should be around 13.8V ± some noise
        assert 12.0 <= telemetry.battery_voltage <= 15.0

        # Fuel level should be around 75% ± some noise
        assert 70.0 <= telemetry.fuel_level_percent <= 80.0

    def test_telemetry_location_matches_config(
        self, config: AgentConfig, generator: SimpleTelemetryGenerator
    ) -> None:
        """Test that location matches initial configuration."""
        telemetry = generator.generate()

        assert telemetry.latitude == config.initial_latitude
        assert telemetry.longitude == config.initial_longitude
        assert telemetry.speed_kmh == 0.0  # Parked

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
        assert telemetry.latitude is not None
        assert telemetry.longitude is not None
        assert telemetry.speed_kmh is not None
        assert telemetry.odometer_km is not None
        assert telemetry.engine_temp_celsius is not None
        assert telemetry.battery_voltage is not None
        assert telemetry.fuel_level_percent is not None
