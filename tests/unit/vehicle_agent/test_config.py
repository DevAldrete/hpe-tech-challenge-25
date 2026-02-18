"""Unit tests for vehicle agent configuration."""

import pytest
from pydantic import ValidationError

from src.models.enums import OperationalStatus, VehicleType
from src.vehicle_agent.config import AgentConfig


class TestAgentConfig:
    """Test suite for AgentConfig."""

    def test_config_valid_creation(self) -> None:
        """Test creating a valid configuration."""
        config = AgentConfig(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
        )

        assert config.vehicle_id == "AMB-001"
        assert config.vehicle_type == VehicleType.AMBULANCE
        assert config.fleet_id == "fleet01"  # Default
        assert config.redis_host == "localhost"  # Default
        assert config.redis_port == 6379  # Default

    def test_config_custom_values(self) -> None:
        """Test configuration with custom values."""
        config = AgentConfig(
            vehicle_id="FIRE-042",
            vehicle_type=VehicleType.FIRE_TRUCK,
            fleet_id="fleet02",
            redis_host="redis.example.com",
            redis_port=6380,
            redis_password="secret",
            telemetry_frequency_hz=5.0,
            initial_latitude=40.7128,
            initial_longitude=-74.0060,
        )

        assert config.vehicle_id == "FIRE-042"
        assert config.vehicle_type == VehicleType.FIRE_TRUCK
        assert config.fleet_id == "fleet02"
        assert config.redis_host == "redis.example.com"
        assert config.redis_port == 6380
        assert config.redis_password == "secret"
        assert config.telemetry_frequency_hz == 5.0
        assert config.initial_latitude == 40.7128
        assert config.initial_longitude == -74.0060

    def test_config_invalid_port(self) -> None:
        """Test that invalid port raises validation error."""
        with pytest.raises(ValidationError):
            AgentConfig(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                redis_port=99999,  # Invalid port
            )

    def test_config_invalid_frequency(self) -> None:
        """Test that invalid frequency raises validation error."""
        with pytest.raises(ValidationError):
            AgentConfig(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                telemetry_frequency_hz=0.0,  # Too low
            )

        with pytest.raises(ValidationError):
            AgentConfig(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                telemetry_frequency_hz=20.0,  # Too high
            )

    def test_config_invalid_latitude(self) -> None:
        """Test that invalid latitude raises validation error."""
        with pytest.raises(ValidationError):
            AgentConfig(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                initial_latitude=100.0,  # Out of range
            )

    def test_config_invalid_longitude(self) -> None:
        """Test that invalid longitude raises validation error."""
        with pytest.raises(ValidationError):
            AgentConfig(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                initial_longitude=200.0,  # Out of range
            )

    def test_get_channel_name_telemetry(self) -> None:
        """Test channel name generation for telemetry."""
        config = AgentConfig(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
            fleet_id="fleet01",
        )

        channel = config.get_channel_name("telemetry")
        assert channel == "aegis:fleet01:telemetry:AMB-001"

    def test_get_channel_name_alerts(self) -> None:
        """Test channel name generation for alerts."""
        config = AgentConfig(
            vehicle_id="FIRE-042",
            vehicle_type=VehicleType.FIRE_TRUCK,
            fleet_id="fleet02",
        )

        channel = config.get_channel_name("alerts")
        assert channel == "aegis:fleet02:alerts:FIRE-042"

    def test_initial_status_default(self) -> None:
        """Test that initial status defaults to IDLE."""
        config = AgentConfig(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
        )

        assert config.initial_status == OperationalStatus.IDLE

    def test_agent_version_default(self) -> None:
        """Test that agent version has a default value."""
        config = AgentConfig(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
        )

        assert config.agent_version == "1.0.0"
