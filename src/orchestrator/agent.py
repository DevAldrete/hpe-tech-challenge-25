"""
Central orchestrator agent for Project AEGIS.

This module contains the OrchestratorAgent which subscribes to all vehicle
telemetry via Redis, maintains the fleet state in memory, and coordinates
emergency dispatch.
"""

import asyncio
import json
from datetime import datetime

import redis.asyncio as redis
import structlog

from src.models.dispatch import Dispatch, VehicleStatusSnapshot
from src.models.emergency import Emergency, EmergencyStatus
from src.models.enums import MessageType, OperationalStatus, VehicleType
from src.models.messages import Message
from src.orchestrator.dispatch_engine import DispatchEngine

logger = structlog.get_logger(__name__)

# Redis channel patterns
TELEMETRY_PATTERN = "aegis:*:telemetry:*"
HEARTBEAT_PATTERN = "aegis:*:heartbeat:*"
ALERTS_PATTERN = "aegis:*:alerts:*"
EMERGENCY_CHANNEL = "aegis:emergencies:new"
DISPATCH_CHANNEL_PREFIX = "aegis:dispatch"


class OrchestratorAgent:
    """Central brain of the AEGIS system.

    Subscribes to all vehicle channels via Redis pub/sub and maintains
    an in-memory fleet state. Processes incoming emergencies and triggers
    dispatch via the DispatchEngine.

    The fleet state is a shared mutable dict updated by telemetry messages
    and read by the DispatchEngine for unit selection.

    Attributes:
        fleet: Dict of vehicle_id -> VehicleStatusSnapshot (in-memory state).
        emergencies: Dict of emergency_id -> Emergency (in-memory).
        dispatches: Dict of emergency_id -> Dispatch (in-memory).
    """

    def __init__(
        self,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_password: str | None = None,
        redis_db: int = 0,
        fleet_id: str = "fleet01",
    ) -> None:
        """Initialize the orchestrator.

        Args:
            redis_host: Redis server hostname.
            redis_port: Redis server port.
            redis_password: Optional Redis password.
            redis_db: Redis database number.
            fleet_id: Fleet identifier for channel naming.
        """
        self._redis_host = redis_host
        self._redis_port = redis_port
        self._redis_password = redis_password
        self._redis_db = redis_db
        self._fleet_id = fleet_id

        self.fleet: dict[str, VehicleStatusSnapshot] = {}
        self.emergencies: dict[str, Emergency] = {}
        self.dispatches: dict[str, Dispatch] = {}

        self.dispatch_engine = DispatchEngine(self.fleet)

        self._redis: redis.Redis | None = None
        self._pubsub: redis.client.PubSub | None = None
        self.running = False

    async def start(self) -> None:
        """Connect to Redis and start background listener task.

        Raises:
            redis.ConnectionError: If Redis is unreachable.
        """
        self._redis = redis.Redis(
            host=self._redis_host,
            port=self._redis_port,
            password=self._redis_password,
            db=self._redis_db,
            decode_responses=True,
        )
        await self._redis.ping()

        self._pubsub = self._redis.pubsub()
        await self._pubsub.psubscribe(
            TELEMETRY_PATTERN,
            HEARTBEAT_PATTERN,
            ALERTS_PATTERN,
            EMERGENCY_CHANNEL,
        )

        self.running = True
        logger.info(
            "orchestrator_started",
            redis_host=self._redis_host,
            fleet_id=self._fleet_id,
        )

    async def stop(self) -> None:
        """Gracefully stop the orchestrator and close Redis connection."""
        self.running = False
        if self._pubsub:
            await self._pubsub.punsubscribe()
            await self._pubsub.close()
        if self._redis:
            await self._redis.aclose()
        logger.info("orchestrator_stopped")

    async def run(self) -> None:
        """Main event loop - listen for Redis messages until stopped.

        Call start() before run(). This method blocks until stop() is called.
        """
        await self.start()
        try:
            async for raw in self._pubsub.listen():  # type: ignore[union-attr]
                if not self.running:
                    break
                if raw["type"] not in ("message", "pmessage"):
                    continue
                await self._handle_raw_message(raw)
        except Exception as e:
            logger.error("orchestrator_error", error=str(e), exc_info=True)
            raise
        finally:
            await self.stop()

    async def _handle_raw_message(self, raw: dict) -> None:
        """Parse and dispatch an incoming Redis pub/sub message.

        Args:
            raw: Raw message dict from redis-py pubsub listener.
        """
        channel: str = raw.get("channel", "") or raw.get("pattern", "") or ""
        data: str = raw.get("data", "")

        if not data or not isinstance(data, str):
            return

        try:
            message = Message.model_validate_json(data)
        except Exception as e:
            logger.warning("message_parse_error", channel=channel, error=str(e))
            return

        if message.message_type == MessageType.TELEMETRY_UPDATE:
            await self._handle_telemetry(message)
        elif message.message_type == MessageType.HEARTBEAT:
            await self._handle_heartbeat(message)
        elif message.message_type == MessageType.ALERT_GENERATED:
            await self._handle_alert(message)
        else:
            logger.debug(
                "unhandled_message_type",
                message_type=message.message_type.value,
                source=message.source,
            )

    async def _handle_telemetry(self, message: Message) -> None:
        """Update fleet state from a telemetry message.

        Args:
            message: Telemetry Message envelope from a vehicle.
        """
        vehicle_id = message.source
        telemetry_data = message.payload.get("telemetry", {})

        snap = self.fleet.get(vehicle_id)
        if snap is None:
            # First time seeing this vehicle - infer type from ID prefix
            vehicle_type = _infer_vehicle_type(vehicle_id)
            snap = VehicleStatusSnapshot(
                vehicle_id=vehicle_id,
                vehicle_type=vehicle_type,
                operational_status=OperationalStatus.IDLE,
            )
            self.fleet[vehicle_id] = snap
            logger.info("new_vehicle_registered", vehicle_id=vehicle_id, type=vehicle_type.value)

        # Update last seen timestamp
        snap.last_seen_at = datetime.utcnow()

        # Update location if present
        if "location" in telemetry_data:
            from src.models.vehicle import GeoLocation

            try:
                snap.location = GeoLocation.model_validate(telemetry_data["location"])
            except Exception:
                pass  # Location parse failure is non-fatal

        # Update key health metrics
        if "battery_voltage" in telemetry_data:
            snap.battery_voltage = float(telemetry_data["battery_voltage"])
        if "fuel_level_percent" in telemetry_data:
            snap.fuel_level_percent = float(telemetry_data["fuel_level_percent"])

        logger.debug("telemetry_processed", vehicle_id=vehicle_id)

    async def _handle_heartbeat(self, message: Message) -> None:
        """Update fleet state from a heartbeat message.

        Args:
            message: Heartbeat Message envelope from a vehicle.
        """
        vehicle_id = message.source
        if vehicle_id in self.fleet:
            self.fleet[vehicle_id].last_seen_at = datetime.utcnow()
            logger.debug("heartbeat_received", vehicle_id=vehicle_id)

    async def _handle_alert(self, message: Message) -> None:
        """Mark a vehicle as having an active alert.

        Args:
            message: Alert Message envelope from a vehicle.
        """
        vehicle_id = message.source
        if vehicle_id in self.fleet:
            self.fleet[vehicle_id].has_active_alert = True
        logger.info("alert_received", vehicle_id=vehicle_id, payload=message.payload)

    async def process_emergency(self, emergency: Emergency) -> Dispatch:
        """Process a new emergency: run dispatch and publish assignments to Redis.

        This is the core coordination method. It:
        1. Stores the emergency.
        2. Runs the DispatchEngine to select nearest available units.
        3. Updates the emergency status.
        4. Publishes assignment messages to each dispatched vehicle.
        5. Publishes a broadcast so all agents know the emergency is taken.

        Args:
            emergency: The newly registered Emergency.

        Returns:
            The resulting Dispatch record.
        """
        self.emergencies[emergency.emergency_id] = emergency

        dispatch = self.dispatch_engine.select_units(emergency)
        self.dispatches[emergency.emergency_id] = dispatch

        if dispatch.units:
            emergency.status = EmergencyStatus.DISPATCHED
            emergency.dispatched_at = datetime.utcnow()
        else:
            emergency.status = EmergencyStatus.DISPATCHING
            logger.warning(
                "no_units_available",
                emergency_id=emergency.emergency_id,
                emergency_type=emergency.emergency_type.value,
            )

        # Publish assignment to each vehicle
        if self._redis:
            for unit in dispatch.units:
                channel = f"aegis:{self._fleet_id}:commands:{unit.vehicle_id}"
                payload = {
                    "command": "dispatch",
                    "emergency_id": emergency.emergency_id,
                    "emergency_type": emergency.emergency_type.value,
                    "location": emergency.location.model_dump(mode="json"),
                    "dispatch_id": dispatch.dispatch_id,
                }
                try:
                    await self._redis.publish(channel, json.dumps(payload))
                except Exception as e:
                    logger.error(
                        "dispatch_publish_failed",
                        vehicle_id=unit.vehicle_id,
                        error=str(e),
                    )

            # Broadcast to all: this emergency has been taken
            broadcast_channel = f"{DISPATCH_CHANNEL_PREFIX}:{emergency.emergency_id}:assigned"
            broadcast_payload = {
                "emergency_id": emergency.emergency_id,
                "dispatch_id": dispatch.dispatch_id,
                "assigned_vehicles": dispatch.vehicle_ids,
            }
            try:
                await self._redis.publish(broadcast_channel, json.dumps(broadcast_payload))
            except Exception as e:
                logger.error("broadcast_failed", emergency_id=emergency.emergency_id, error=str(e))

        logger.info(
            "emergency_processed",
            emergency_id=emergency.emergency_id,
            status=emergency.status.value,
            units_dispatched=len(dispatch.units),
            vehicle_ids=dispatch.vehicle_ids,
        )

        return dispatch

    async def resolve_emergency(self, emergency_id: str) -> list[str]:
        """Mark an emergency as resolved and release its units back to IDLE.

        Args:
            emergency_id: The ID of the emergency to resolve.

        Returns:
            List of vehicle_ids that were released.

        Raises:
            KeyError: If the emergency_id is not found.
        """
        emergency = self.emergencies[emergency_id]
        emergency.status = EmergencyStatus.RESOLVED
        emergency.resolved_at = datetime.utcnow()

        released = self.dispatch_engine.release_units(emergency_id)

        # Publish resolution broadcast
        if self._redis:
            channel = f"{DISPATCH_CHANNEL_PREFIX}:{emergency_id}:resolved"
            payload = {"emergency_id": emergency_id, "released_vehicles": released}
            try:
                await self._redis.publish(channel, json.dumps(payload))
            except Exception as e:
                logger.error("resolve_broadcast_failed", emergency_id=emergency_id, error=str(e))

        logger.info(
            "emergency_resolved",
            emergency_id=emergency_id,
            released_vehicles=released,
        )
        return released

    def get_fleet_summary(self) -> dict:
        """Return a summary of the current fleet state.

        Returns:
            Dict with total count, available count, and per-type breakdown.
        """
        total = len(self.fleet)
        available = sum(1 for s in self.fleet.values() if s.is_available)
        by_type: dict[str, dict[str, int]] = {}

        for snap in self.fleet.values():
            key = snap.vehicle_type.value
            if key not in by_type:
                by_type[key] = {"total": 0, "available": 0}
            by_type[key]["total"] += 1
            if snap.is_available:
                by_type[key]["available"] += 1

        return {
            "total_vehicles": total,
            "available_vehicles": available,
            "active_emergencies": sum(
                1
                for e in self.emergencies.values()
                if e.status not in (EmergencyStatus.RESOLVED, EmergencyStatus.CANCELLED)
            ),
            "by_type": by_type,
        }


def _infer_vehicle_type(vehicle_id: str) -> VehicleType:
    """Infer vehicle type from vehicle_id prefix convention.

    Args:
        vehicle_id: Vehicle identifier (e.g. AMB-001, FIRE-002, POL-003).

    Returns:
        Best-guess VehicleType, defaults to AMBULANCE if unknown.
    """
    vid = vehicle_id.upper()
    if vid.startswith("AMB"):
        return VehicleType.AMBULANCE
    if vid.startswith("FIRE"):
        return VehicleType.FIRE_TRUCK
    if vid.startswith("POL"):
        return VehicleType.POLICE
    logger.warning("unknown_vehicle_id_prefix", vehicle_id=vehicle_id)
    return VehicleType.AMBULANCE
