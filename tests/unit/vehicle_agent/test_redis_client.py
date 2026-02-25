"""Unit tests for Redis client."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest

from src.models.alerts import PredictiveAlert
from src.models.enums import AlertSeverity, FailureCategory, VehicleType
from src.models.telemetry import VehicleTelemetry
from src.vehicle_agent.config import AgentConfig
from src.vehicle_agent.redis_client import RedisClient


class TestRedisClient:
    """Test suite for RedisClient."""

    @pytest.fixture
    def config(self) -> AgentConfig:
        """Create a test configuration."""
        return AgentConfig(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
        )

    @pytest.fixture
    def redis_client(self, config: AgentConfig) -> RedisClient:
        """Create a Redis client."""
        return RedisClient(config)

    @pytest.fixture
    def sample_telemetry(self, config: AgentConfig) -> VehicleTelemetry:
        """Create sample telemetry data."""
        return VehicleTelemetry(
            vehicle_id=config.vehicle_id,
            timestamp=datetime.now(timezone.utc),
            latitude=37.7749,
            longitude=-122.4194,
            speed_kmh=65.0,
            odometer_km=45678.9,
            engine_temp_celsius=90.0,
            battery_voltage=13.8,
            fuel_level_percent=75.0,
        )

    def test_client_initialization(self, config: AgentConfig) -> None:
        """Test client initializes correctly."""
        client = RedisClient(config)

        assert client.config == config
        assert client.redis is None
        assert client.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_success(self, redis_client: RedisClient) -> None:
        """Test successful Redis connection."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_redis.return_value = mock_instance

            await redis_client.connect()

            assert redis_client.is_connected is True
            mock_instance.ping.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_failure(self, redis_client: RedisClient) -> None:
        """Test Redis connection failure."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock(side_effect=Exception("Connection failed"))
            mock_redis.return_value = mock_instance

            with pytest.raises(Exception, match="Connection failed"):
                await redis_client.connect()

            assert redis_client.is_connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, redis_client: RedisClient) -> None:
        """Test disconnecting from Redis."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.close = AsyncMock()
            mock_redis.return_value = mock_instance

            await redis_client.connect()
            await redis_client.disconnect()

            assert redis_client.is_connected is False
            mock_instance.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_telemetry_not_connected(
        self, redis_client: RedisClient, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test publishing telemetry when not connected raises error."""
        with pytest.raises(RuntimeError, match="not connected"):
            await redis_client.publish_telemetry(sample_telemetry)

    @pytest.mark.asyncio
    async def test_publish_telemetry_success(
        self, redis_client: RedisClient, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test successfully publishing telemetry."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.publish = AsyncMock()
            mock_redis.return_value = mock_instance

            await redis_client.connect()
            await redis_client.publish_telemetry(sample_telemetry)

            # Verify publish was called
            mock_instance.publish.assert_called_once()

            # Check the channel name
            call_args = mock_instance.publish.call_args
            channel = call_args[0][0]
            assert channel == "aegis:fleet01:telemetry:AMB-001"

    @pytest.mark.asyncio
    async def test_publish_telemetry_handles_error(
        self, redis_client: RedisClient, sample_telemetry: VehicleTelemetry
    ) -> None:
        """Test that publish errors are handled gracefully."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.publish = AsyncMock(side_effect=Exception("Publish failed"))
            mock_redis.return_value = mock_instance

            await redis_client.connect()

            # Should not raise, just log error
            await redis_client.publish_telemetry(sample_telemetry)

    @pytest.mark.asyncio
    async def test_is_connected_property(self, redis_client: RedisClient) -> None:
        """Test is_connected property."""
        assert redis_client.is_connected is False

        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_redis.return_value = mock_instance

            await redis_client.connect()
            assert redis_client.is_connected is True

            await redis_client.disconnect()
            assert redis_client.is_connected is False

    @pytest.mark.asyncio
    async def test_publish_alert_not_connected(self, redis_client: RedisClient) -> None:
        """Test publishing alert when not connected raises error."""
        alert = PredictiveAlert(
            vehicle_id="AMB-001",
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverity.WARNING,
            category=FailureCategory.ENGINE,
            component="engine",
            failure_probability=0.65,
            confidence=0.85,
            predicted_failure_min_hours=2.0,
            predicted_failure_max_hours=8.0,
            predicted_failure_likely_hours=4.0,
            can_complete_current_mission=True,
            safe_to_operate=True,
            recommended_action="Test action",
            contributing_factors=["Test factor"],
            related_telemetry={},
        )

        with pytest.raises(RuntimeError, match="not connected"):
            await redis_client.publish_alert(alert)

    @pytest.mark.asyncio
    async def test_publish_alert_success_warning(self, redis_client: RedisClient) -> None:
        """Test successfully publishing WARNING alert."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.publish = AsyncMock()
            mock_redis.return_value = mock_instance

            await redis_client.connect()

            alert = PredictiveAlert(
                vehicle_id="AMB-001",
                timestamp=datetime.now(timezone.utc),
                severity=AlertSeverity.WARNING,
                category=FailureCategory.ENGINE,
                component="engine",
                failure_probability=0.65,
                confidence=0.85,
                predicted_failure_min_hours=2.0,
                predicted_failure_max_hours=8.0,
                predicted_failure_likely_hours=4.0,
                can_complete_current_mission=True,
                safe_to_operate=True,
                recommended_action="Test action",
                contributing_factors=["Test factor"],
                related_telemetry={},
            )

            await redis_client.publish_alert(alert)

            # Verify publish was called
            mock_instance.publish.assert_called_once()

            # Check the channel name
            call_args = mock_instance.publish.call_args
            channel = call_args[0][0]
            assert channel == "aegis:fleet01:alerts:AMB-001"

    @pytest.mark.asyncio
    async def test_publish_alert_success_critical(self, redis_client: RedisClient) -> None:
        """Test successfully publishing CRITICAL alert."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.publish = AsyncMock()
            mock_redis.return_value = mock_instance

            await redis_client.connect()

            alert = PredictiveAlert(
                vehicle_id="AMB-001",
                timestamp=datetime.now(timezone.utc),
                severity=AlertSeverity.CRITICAL,
                category=FailureCategory.ENGINE,
                component="engine",
                failure_probability=0.95,
                confidence=0.98,
                predicted_failure_min_hours=0.5,
                predicted_failure_max_hours=2.0,
                predicted_failure_likely_hours=1.0,
                can_complete_current_mission=False,
                safe_to_operate=False,
                recommended_action="STOP IMMEDIATELY",
                contributing_factors=["Test factor"],
                related_telemetry={},
            )

            await redis_client.publish_alert(alert)

            # Verify publish was called
            mock_instance.publish.assert_called_once()

    @pytest.mark.asyncio
    async def test_publish_alert_handles_error(self, redis_client: RedisClient) -> None:
        """Test that alert publish errors are handled gracefully."""
        with patch("redis.asyncio.Redis") as mock_redis:
            mock_instance = AsyncMock()
            mock_instance.ping = AsyncMock()
            mock_instance.publish = AsyncMock(side_effect=Exception("Publish failed"))
            mock_redis.return_value = mock_instance

            await redis_client.connect()

            alert = PredictiveAlert(
                vehicle_id="AMB-001",
                timestamp=datetime.now(timezone.utc),
                severity=AlertSeverity.WARNING,
                category=FailureCategory.ENGINE,
                component="engine",
                failure_probability=0.65,
                confidence=0.85,
                predicted_failure_min_hours=2.0,
                predicted_failure_max_hours=8.0,
                predicted_failure_likely_hours=4.0,
                can_complete_current_mission=True,
                safe_to_operate=True,
                recommended_action="Test action",
                contributing_factors=["Test factor"],
                related_telemetry={},
            )

            # Should not raise, just log error
            await redis_client.publish_alert(alert)
