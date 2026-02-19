"""
Telemetry generation for vehicle agents.

This module generates synthetic vehicle telemetry data for simulation purposes.
Phase 1: Simple constant values with Gaussian noise.
"""

import random
from datetime import UTC, datetime

import structlog

from src.models.telemetry import VehicleTelemetry
from src.models.vehicle import GeoLocation
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
        self.sequence_number = 0

        # Baseline values for idle vehicle at station
        self.baselines = {
            # Engine & Powertrain
            "engine_temp_celsius": 90.0,
            "engine_rpm": 800,  # Idle RPM
            "coolant_temp_celsius": 85.0,
            "oil_pressure_psi": 45.0,
            "oil_temp_celsius": 90.0,
            "transmission_temp_celsius": 75.0,
            "throttle_position_percent": 0.0,
            # Electrical
            "battery_voltage": 13.8,
            "battery_current_amps": -2.0,  # Slight discharge at idle
            "alternator_voltage": 14.2,
            "battery_state_of_charge_percent": 95.0,
            "battery_health_percent": 92.0,
            # Fuel
            "fuel_level_percent": 75.0,
            "fuel_level_liters": 30.0,
            "fuel_consumption_lph": 1.5,  # Idle consumption
            # Braking
            "brake_fluid_level_percent": 100.0,
            # Environmental
            "cabin_temp_celsius": 22.0,
            "exterior_temp_celsius": 20.0,
            "humidity_percent": 50.0,
            # Location
            "odometer_km": 45678.9,
        }

        # Noise levels (as fraction of baseline value)
        self.noise_levels = {
            "engine_temp_celsius": 0.02,  # ±2%
            "engine_rpm": 0.06,  # ±6% (more variation at idle)
            "coolant_temp_celsius": 0.02,
            "oil_pressure_psi": 0.03,
            "oil_temp_celsius": 0.02,
            "transmission_temp_celsius": 0.03,
            "throttle_position_percent": 0.0,  # No throttle at idle
            "battery_voltage": 0.02,
            "battery_current_amps": 0.15,
            "alternator_voltage": 0.01,
            "battery_state_of_charge_percent": 0.01,
            "battery_health_percent": 0.005,
            "fuel_level_percent": 0.01,
            "fuel_level_liters": 0.01,
            "fuel_consumption_lph": 0.10,
            "brake_fluid_level_percent": 0.005,
            "cabin_temp_celsius": 0.03,
            "exterior_temp_celsius": 0.02,
            "humidity_percent": 0.02,
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
        self.sequence_number += 1

        # Generate location (fixed for now, parked at station)
        location = GeoLocation(
            latitude=self.config.initial_latitude,
            longitude=self.config.initial_longitude,
            altitude=self.config.initial_altitude,
            accuracy=5.0,
            heading=0.0,
            speed_kmh=0.0,  # Parked
            timestamp=datetime.now(UTC),
        )

        # Generate telemetry with noise
        telemetry = VehicleTelemetry(
            vehicle_id=self.config.vehicle_id,
            timestamp=datetime.now(UTC),
            sequence_number=self.sequence_number,
            location=location,
            odometer_km=self._add_noise("odometer_km"),
            # Engine & Powertrain
            engine_temp_celsius=self._add_noise("engine_temp_celsius"),
            engine_rpm=int(self._add_noise("engine_rpm")),
            coolant_temp_celsius=self._add_noise("coolant_temp_celsius"),
            oil_pressure_psi=self._add_noise("oil_pressure_psi"),
            oil_temp_celsius=self._add_noise("oil_temp_celsius"),
            transmission_temp_celsius=self._add_noise("transmission_temp_celsius"),
            throttle_position_percent=self._add_noise("throttle_position_percent"),
            # Electrical System
            battery_voltage=self._add_noise("battery_voltage"),
            battery_current_amps=self._add_noise("battery_current_amps"),
            alternator_voltage=self._add_noise("alternator_voltage"),
            battery_state_of_charge_percent=self._add_noise("battery_state_of_charge_percent"),
            battery_health_percent=self._add_noise("battery_health_percent"),
            # Fuel System
            fuel_level_percent=self._add_noise("fuel_level_percent"),
            fuel_level_liters=self._add_noise("fuel_level_liters"),
            fuel_consumption_lph=self._add_noise("fuel_consumption_lph"),
            fuel_economy_kml=None,  # Not moving
            # Braking System
            brake_pad_thickness_mm={
                "front_left": 8.0,
                "front_right": 8.0,
                "rear_left": 9.0,
                "rear_right": 9.0,
            },
            brake_fluid_level_percent=self._add_noise("brake_fluid_level_percent"),
            brake_temp_celsius={
                "front_left": 25.0,
                "front_right": 25.0,
                "rear_left": 25.0,
                "rear_right": 25.0,
            },
            abs_active=False,
            # Tires
            tire_pressure_psi={
                "front_left": self._add_noise_raw(80.0, 0.02),
                "front_right": self._add_noise_raw(80.0, 0.02),
                "rear_left": self._add_noise_raw(80.0, 0.02),
                "rear_right": self._add_noise_raw(80.0, 0.02),
            },
            tire_temp_celsius={
                "front_left": 25.0,
                "front_right": 25.0,
                "rear_left": 25.0,
                "rear_right": 25.0,
            },
            # Suspension & Chassis
            suspension_travel_mm={},
            vibration_g_force={"x": 0.01, "y": 0.01, "z": 1.0},  # Minimal vibration at idle
            # Environmental
            cabin_temp_celsius=self._add_noise("cabin_temp_celsius"),
            exterior_temp_celsius=self._add_noise("exterior_temp_celsius"),
            humidity_percent=self._add_noise("humidity_percent"),
            # Emergency Equipment
            siren_active=False,
            lights_active=False,
            equipment_status={},
            # Diagnostics
            active_dtc_codes=[],
        )

        logger.debug(
            "telemetry_generated",
            vehicle_id=self.config.vehicle_id,
            sequence=self.sequence_number,
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
