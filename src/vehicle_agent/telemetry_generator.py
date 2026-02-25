"""
Telemetry generation for vehicle agents.

This module generates synthetic vehicle telemetry data for simulation purposes.
Phase 1: Simple constant values with Gaussian noise.
"""

import random
from datetime import UTC, datetime

import structlog

from src.models.telemetry import VehicleTelemetry
from src.vehicle_agent.config import AgentConfig

logger = structlog.get_logger(__name__)


class SimpleTelemetryGenerator:
    """Simple telemetry generator using constant baseline values with noise.

    Generates realistic-looking telemetry by adding small random variations
    to baseline constant values. This is sufficient for Phase 1 POC.
    """

    def __init__(self, config: AgentConfig) -> None:
        """
        Initialize telemetry generator.

        Args:
            config: Agent configuration containing vehicle identity and initial state
        """
        self.config = config

        # Baseline values for idle vehicle at station
        self.baselines = {
            "engine_temp_celsius": 90.0,
            "battery_voltage": 13.8,
            "fuel_level_percent": 75.0,
            "odometer_km": 45678.9,
        }

        # Noise levels (as fraction of baseline value)
        self.noise_levels = {
            "engine_temp_celsius": 0.02,  # ±2%
            "battery_voltage": 0.02,
            "fuel_level_percent": 0.01,
            "odometer_km": 0.0,  # Doesn't change when parked
        }

    def generate(self) -> VehicleTelemetry:
        """
        Generate a single telemetry reading with current timestamp.

        Returns:
            VehicleTelemetry object with all required fields

        Example:
            >>> generator = SimpleTelemetryGenerator(config)
            >>> telemetry = generator.generate()
            >>> print(telemetry.engine_temp_celsius)
            90.5  # 90.0 ± noise
        """

        # Generate telemetry with noise
        telemetry = VehicleTelemetry(
            vehicle_id=self.config.vehicle_id,
            timestamp=datetime.now(UTC),
            latitude=self.config.initial_latitude,
            longitude=self.config.initial_longitude,
            speed_kmh=0.0,  # Parked
            odometer_km=self._add_noise("odometer_km"),
            engine_temp_celsius=self._add_noise("engine_temp_celsius"),
            battery_voltage=self._add_noise("battery_voltage"),
            fuel_level_percent=self._add_noise("fuel_level_percent"),
        )

        logger.debug(
            "telemetry_generated",
            vehicle_id=self.config.vehicle_id,
        )

        return telemetry

    def _add_noise(self, metric: str) -> float:
        """
        Add Gaussian noise to a baseline metric value.

        Args:
            metric: Name of the metric in self.baselines

        Returns:
            Baseline value with added noise
        """
        baseline = self.baselines[metric]
        noise_level = self.noise_levels[metric]
        return self._add_noise_raw(baseline, noise_level)

    def _add_noise_raw(self, baseline: float, noise_level: float) -> float:
        """
        Add Gaussian noise to a raw value.

        Args:
            baseline: Base value
            noise_level: Noise as fraction of baseline (e.g., 0.02 = ±2%)

        Returns:
            Value with added Gaussian noise, clamped to reasonable ranges
        """
        if noise_level == 0.0:
            return baseline

        # Calculate standard deviation (noise_level is ~±2σ for 95% confidence)
        std_dev = abs(baseline * noise_level) / 2.0

        # Add Gaussian noise
        noise = random.gauss(0, std_dev)
        result = baseline + noise

        # Clamp to reasonable ranges to avoid validation errors
        # Percentages should never exceed 100 or go below 0
        if baseline <= 100.0 and baseline >= 0.0:
            result = max(0.0, min(100.0, result))

        return result
