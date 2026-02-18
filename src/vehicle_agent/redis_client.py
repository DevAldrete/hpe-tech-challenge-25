"""
Redis communication layer for vehicle agents.

This module handles async pub/sub communication with Redis for telemetry streaming.
"""

from typing import Any

import redis.asyncio as redis
import structlog

from src.models.alerts import PredictiveAlert
from src.models.messages import HeartbeatPayload, Message, MessagePriority, MessageType
from src.models.telemetry import VehicleTelemetry
from src.vehicle_agent.config import AgentConfig

logger = structlog.get_logger(__name__)


class RedisClient:
    """Async Redis client for vehicle agent communication.

    Handles publishing telemetry, alerts, status changes, and heartbeats to Redis
    using the AEGIS communication protocol.
    """

    def __init__(self, config: AgentConfig) -> None:
        """
        Initialize Redis client.

        Args:
            config: Agent configuration containing Redis connection details
        """
        self.config = config
        self.redis: redis.Redis | None = None
        self._connected = False

    async def connect(self) -> None:
        """
        Establish connection to Redis server.

        Raises:
            redis.ConnectionError: If connection fails
        """
        try:
            self.redis = redis.Redis(
                host=self.config.redis_host,
                port=self.config.redis_port,
                password=self.config.redis_password,
                db=self.config.redis_db,
                decode_responses=True,  # Decode bytes to strings
            )

            # Test connection
            await self.redis.ping()
            self._connected = True

            logger.info(
                "redis_connected",
                vehicle_id=self.config.vehicle_id,
                host=self.config.redis_host,
                port=self.config.redis_port,
            )

        except Exception as e:
            logger.error(
                "redis_connection_failed",
                vehicle_id=self.config.vehicle_id,
                error=str(e),
            )
            raise

    async def disconnect(self) -> None:
        """Close Redis connection gracefully."""
        if self.redis:
            await self.redis.close()
            self._connected = False
            logger.info("redis_disconnected", vehicle_id=self.config.vehicle_id)

    async def publish_telemetry(self, telemetry: VehicleTelemetry) -> None:
        """
        Publish vehicle telemetry to Redis channel.

        Args:
            telemetry: VehicleTelemetry data to publish

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self._connected or not self.redis:
            raise RuntimeError("Redis client not connected")

        # Wrap telemetry in Message envelope
        message = Message(
            message_type=MessageType.TELEMETRY_UPDATE,
            source=self.config.vehicle_id,
            destination="orchestrator",
            priority=MessagePriority.NORMAL,
            correlation_id=None,
            payload={"telemetry": telemetry.model_dump(mode="json")},
        )

        channel = self.config.get_channel_name("telemetry")

        try:
            # Publish to Redis channel
            await self.redis.publish(channel, message.model_dump_json())

            logger.debug(
                "telemetry_published",
                vehicle_id=self.config.vehicle_id,
                sequence=telemetry.sequence_number,
                channel=channel,
            )

        except Exception as e:
            logger.error(
                "telemetry_publish_failed",
                vehicle_id=self.config.vehicle_id,
                error=str(e),
            )
            # Don't raise - continue operating even if publish fails
            # In production, would buffer and retry

    async def publish_message(
        self, channel_type: str, message_type: MessageType, payload: dict[str, Any]
    ) -> None:
        """
        Generic method to publish any message type to Redis.

        Args:
            channel_type: Type of channel (alerts, status, heartbeat, etc.)
            message_type: MessageType enum value
            payload: Message payload dictionary

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self._connected or not self.redis:
            raise RuntimeError("Redis client not connected")

        message = Message(
            message_type=message_type,
            source=self.config.vehicle_id,
            destination="orchestrator",
            priority=MessagePriority.NORMAL,
            correlation_id=None,
            payload=payload,
        )

        channel = self.config.get_channel_name(channel_type)

        try:
            await self.redis.publish(channel, message.model_dump_json())

            logger.debug(
                "message_published",
                vehicle_id=self.config.vehicle_id,
                message_type=message_type.value,
                channel=channel,
            )

        except Exception as e:
            logger.error(
                "message_publish_failed",
                vehicle_id=self.config.vehicle_id,
                message_type=message_type.value,
                error=str(e),
            )

    async def publish_alert(self, alert: PredictiveAlert) -> None:
        """
        Publish a predictive alert to Redis channel.

        Args:
            alert: PredictiveAlert to publish

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self._connected or not self.redis:
            raise RuntimeError("Redis client not connected")

        # Wrap alert in Message envelope with HIGH priority
        message = Message(
            message_type=MessageType.ALERT_GENERATED,
            source=self.config.vehicle_id,
            destination="orchestrator",
            priority=MessagePriority.HIGH
            if alert.severity == "warning"
            else MessagePriority.CRITICAL,
            correlation_id=None,
            payload={"alert": alert.model_dump(mode="json")},
        )

        channel = self.config.get_channel_name("alerts")

        try:
            # Publish to Redis channel
            await self.redis.publish(channel, message.model_dump_json())

            logger.info(
                "alert_published",
                vehicle_id=self.config.vehicle_id,
                alert_id=alert.alert_id,
                severity=alert.severity.value,
                component=alert.component,
                channel=channel,
            )

        except Exception as e:
            logger.error(
                "alert_publish_failed",
                vehicle_id=self.config.vehicle_id,
                alert_id=alert.alert_id,
                error=str(e),
            )
            # Don't raise - alerts should not crash the agent

    async def publish_heartbeat(
        self,
        uptime_seconds: int,
        last_telemetry_sequence: int,
        agent_version: str = "1.0.0",
    ) -> None:
        """
        Publish heartbeat message to Redis channel.

        Args:
            uptime_seconds: Seconds since agent started
            last_telemetry_sequence: Last telemetry sequence number sent
            agent_version: Agent software version

        Raises:
            RuntimeError: If not connected to Redis
        """
        if not self._connected or not self.redis:
            raise RuntimeError("Redis client not connected")

        # Create heartbeat payload
        heartbeat = HeartbeatPayload(
            vehicle_id=self.config.vehicle_id,
            uptime_seconds=uptime_seconds,
            last_telemetry_sequence=last_telemetry_sequence,
            agent_version=agent_version,
        )

        # Wrap heartbeat in Message envelope
        message = Message(
            message_type=MessageType.HEARTBEAT,
            source=self.config.vehicle_id,
            destination="orchestrator",
            priority=MessagePriority.LOW,
            correlation_id=None,
            payload=heartbeat.model_dump(mode="json"),
        )

        channel = self.config.get_channel_name("heartbeat")

        try:
            # Publish to Redis channel
            await self.redis.publish(channel, message.model_dump_json())

            logger.debug(
                "heartbeat_published",
                vehicle_id=self.config.vehicle_id,
                uptime_seconds=uptime_seconds,
                channel=channel,
            )

        except Exception as e:
            logger.error(
                "heartbeat_publish_failed",
                vehicle_id=self.config.vehicle_id,
                error=str(e),
            )
            # Don't raise - heartbeats should not crash the agent

    @property
    def is_connected(self) -> bool:
        """Check if Redis client is connected."""
        return self._connected
