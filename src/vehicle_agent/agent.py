"""
Main vehicle agent orchestrator.

This module contains the VehicleAgent class which coordinates all subsystems
and manages the main event loop.
"""

import asyncio
import signal
from typing import Any

import structlog

from src.vehicle_agent.anomaly_detector import AnomalyDetector
from src.vehicle_agent.config import AgentConfig
from src.vehicle_agent.failure_injector import FailureInjector
from src.vehicle_agent.redis_client import RedisClient
from src.vehicle_agent.telemetry_generator import SimpleTelemetryGenerator

logger = structlog.get_logger(__name__)


class VehicleAgent:
    """Main vehicle agent orchestrator.

    Coordinates telemetry generation, Redis communication, and manages the
    agent lifecycle (start, run, stop).

    The agent runs a main loop at the configured frequency (default 1 Hz),
    generating and publishing telemetry data to Redis.
    """

    def __init__(self, config: AgentConfig) -> None:
        """
        Initialize vehicle agent.

        Args:
            config: Agent configuration
        """
        self.config = config
        self.running = False
        self.uptime_seconds = 0.0
        self.heartbeat_counter = 0

        # Initialize components
        self.redis_client = RedisClient(config)
        self.telemetry_generator = SimpleTelemetryGenerator(config)
        self.failure_injector = FailureInjector()
        self.anomaly_detector = AnomalyDetector(config.vehicle_id)

        logger.info(
            "agent_initialized",
            vehicle_id=config.vehicle_id,
            vehicle_type=config.vehicle_type.value,
            fleet_id=config.fleet_id,
        )

    async def start(self) -> None:
        """
        Start the vehicle agent.

        Establishes Redis connection and prepares for operation.

        Raises:
            RuntimeError: If agent is already running
            redis.ConnectionError: If Redis connection fails
        """
        if self.running:
            raise RuntimeError("Agent is already running")

        logger.info("agent_starting", vehicle_id=self.config.vehicle_id)

        # Connect to Redis
        await self.redis_client.connect()

        self.running = True
        logger.info("agent_started", vehicle_id=self.config.vehicle_id)

    async def stop(self) -> None:
        """Stop the vehicle agent gracefully."""
        if not self.running:
            return

        logger.info("agent_stopping", vehicle_id=self.config.vehicle_id)

        self.running = False

        # Disconnect from Redis
        await self.redis_client.disconnect()

        logger.info(
            "agent_stopped",
            vehicle_id=self.config.vehicle_id,
            total_uptime_seconds=self.uptime_seconds,
        )

    async def run(self) -> None:
        """
        Main agent loop.

        Runs continuously at the configured telemetry frequency, generating
        and publishing telemetry data. Handles graceful shutdown on signals.

        Example:
            >>> agent = VehicleAgent(config)
            >>> await agent.run()  # Runs until stopped
        """
        # Setup signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()

        def signal_handler() -> None:
            logger.info("shutdown_signal_received", vehicle_id=self.config.vehicle_id)
            self.running = False

        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)

        # Start the agent
        await self.start()

        # Calculate tick interval from frequency
        tick_interval = 1.0 / self.config.telemetry_frequency_hz

        logger.info(
            "agent_running",
            vehicle_id=self.config.vehicle_id,
            frequency_hz=self.config.telemetry_frequency_hz,
            tick_interval_sec=tick_interval,
        )

        # Main event loop
        try:
            while self.running:
                tick_start = asyncio.get_event_loop().time()

                # Execute one tick
                await self._tick()

                # Calculate sleep time to maintain frequency
                tick_elapsed = asyncio.get_event_loop().time() - tick_start
                sleep_time = max(0, tick_interval - tick_elapsed)

                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)

                # Update uptime
                self.uptime_seconds += tick_interval

        except Exception as e:
            logger.error(
                "agent_error",
                vehicle_id=self.config.vehicle_id,
                error=str(e),
                exc_info=True,
            )
            raise
        finally:
            # Ensure cleanup happens
            await self.stop()

    async def _tick(self) -> None:
        """
        Execute one tick of the main loop.

        This method is called every tick interval and:
        1. Generates telemetry
        2. Applies active failure scenarios
        3. Detects anomalies and generates alerts
        4. Publishes telemetry and alerts to Redis
        5. Publishes heartbeat every 10 seconds
        """
        try:
            # 1. Generate baseline telemetry
            telemetry = self.telemetry_generator.generate()

            # 2. Apply active failure scenarios
            telemetry = self.failure_injector.apply_failures(telemetry)

            # 3. Detect anomalies and generate alerts
            alerts = self.anomaly_detector.analyze(telemetry)

            # 4. Publish telemetry to Redis
            await self.redis_client.publish_telemetry(telemetry)

            # 5. Publish alerts if any were generated
            for alert in alerts:
                await self.redis_client.publish_alert(alert)
                logger.warning(
                    "alert_generated",
                    vehicle_id=self.config.vehicle_id,
                    alert_id=alert.alert_id,
                    severity=alert.severity.value,
                    component=alert.component,
                )

            # 6. Publish heartbeat every 10 seconds (10 ticks at 1 Hz)
            self.heartbeat_counter += 1
            if self.heartbeat_counter >= 10:
                await self.redis_client.publish_heartbeat(
                    uptime_seconds=int(self.uptime_seconds),
                    last_telemetry_sequence=telemetry.sequence_number,
                )
                self.heartbeat_counter = 0

        except Exception as e:
            # Log error but continue running
            logger.error(
                "tick_error",
                vehicle_id=self.config.vehicle_id,
                error=str(e),
            )
            # Don't raise - we want to keep the agent running

    def get_status(self) -> dict[str, Any]:
        """
        Get current agent status.

        Returns:
            Dictionary containing agent status information
        """
        return {
            "vehicle_id": self.config.vehicle_id,
            "vehicle_type": self.config.vehicle_type.value,
            "running": self.running,
            "uptime_seconds": self.uptime_seconds,
            "redis_connected": self.redis_client.is_connected,
            "sequence_number": self.telemetry_generator.sequence_number,
        }
