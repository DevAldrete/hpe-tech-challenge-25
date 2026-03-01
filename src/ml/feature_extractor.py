"""
Feature extraction from sliding windows of telemetry data.
"""

from collections import deque

import numpy as np

from src.models.telemetry import VehicleTelemetry


class FeatureExtractor:
    """Extracts features from a sliding window of vehicle telemetry."""

    def __init__(self, window_size: int = 10) -> None:
        """
        Initialize the feature extractor.

        Args:
            window_size: Number of telemetry points to keep in the sliding window.
        """
        self.window_size = window_size
        self.history: deque[VehicleTelemetry] = deque(maxlen=window_size)

    def add_telemetry(self, telemetry: VehicleTelemetry) -> None:
        """Add a new telemetry point to the window."""
        self.history.append(telemetry)

    def extract_features(self) -> dict[str, float] | None:
        """
        Extract features from the current sliding window.

        Returns:
            Dictionary of features, or None if window is not full.
        """
        if len(self.history) < self.window_size:
            return None

        # Extract basic arrays
        engine_temps = [t.engine_temp_celsius for t in self.history]
        battery_volts = [t.battery_voltage for t in self.history]
        fuel_levels = [t.fuel_level_percent for t in self.history]
        speeds = [t.speed_kmh for t in self.history]

        features = {}

        # Engine Temperature features
        features["engine_temp_mean"] = float(np.mean(engine_temps))
        features["engine_temp_std"] = float(np.std(engine_temps))
        features["engine_temp_max"] = float(np.max(engine_temps))
        features["engine_temp_roc"] = float(engine_temps[-1] - engine_temps[0])

        # Battery Voltage features
        features["battery_voltage_mean"] = float(np.mean(battery_volts))
        features["battery_voltage_std"] = float(np.std(battery_volts))
        features["battery_voltage_min"] = float(np.min(battery_volts))
        features["battery_voltage_roc"] = float(battery_volts[-1] - battery_volts[0])

        # Fuel Level features
        features["fuel_level_mean"] = float(np.mean(fuel_levels))
        features["fuel_level_std"] = float(np.std(fuel_levels))
        features["fuel_level_roc"] = float(fuel_levels[-1] - fuel_levels[0])

        # Speed features
        features["speed_mean"] = float(np.mean(speeds))

        return features
