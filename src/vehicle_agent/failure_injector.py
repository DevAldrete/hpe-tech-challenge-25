"""
Failure injection system for vehicle simulation.

Modifies telemetry based on active failure scenarios to simulate realistic degradation.
"""

from datetime import datetime, UTC

from src.models.enums import FailureScenario
from src.models.telemetry import VehicleTelemetry


class FailureInjector:
    """Injects failure scenarios into vehicle telemetry."""

    def __init__(self) -> None:
        """Initialize the failure injector."""
        self.active_scenarios: dict[FailureScenario, datetime] = {}

    def activate_scenario(self, scenario: FailureScenario) -> None:
        """
        Activate a failure scenario.

        Args:
            scenario: The failure scenario to activate
        """
        self.active_scenarios[scenario] = datetime.now(UTC)

    def deactivate_scenario(self, scenario: FailureScenario) -> None:
        """
        Deactivate a failure scenario.

        Args:
            scenario: The failure scenario to deactivate
        """
        self.active_scenarios.pop(scenario, None)

    def get_time_since_activation(self, scenario: FailureScenario) -> float:
        """
        Get seconds since a scenario was activated.

        Args:
            scenario: The failure scenario to check

        Returns:
            Seconds since activation, or 0.0 if not active
        """
        if scenario not in self.active_scenarios:
            return 0.0
        elapsed = datetime.now(UTC) - self.active_scenarios[scenario]
        return elapsed.total_seconds()

    def apply_failures(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply all active failure scenarios to telemetry.

        Args:
            telemetry: Original telemetry data

        Returns:
            Modified telemetry with failures applied
        """
        modified = telemetry.model_copy(deep=True)

        for scenario in self.active_scenarios:
            if scenario == FailureScenario.ENGINE_OVERHEAT:
                modified = self._apply_engine_overheat(modified)
            elif scenario == FailureScenario.BATTERY_DEGRADATION:
                modified = self._apply_battery_degradation(modified)
            elif scenario == FailureScenario.FUEL_LEAK:
                modified = self._apply_fuel_leak(modified)

        return modified

    def _apply_engine_overheat(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply engine overheat scenario.
        """
        elapsed_minutes = self.get_time_since_activation(FailureScenario.ENGINE_OVERHEAT) / 60.0

        # Temperature rise: +2°C per minute from baseline
        temp_increase = elapsed_minutes * 2.0
        telemetry.engine_temp_celsius = min(90.0 + temp_increase, 150.0)

        return telemetry

    def _apply_battery_degradation(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply battery degradation scenario.
        """
        elapsed_minutes = self.get_time_since_activation(FailureScenario.BATTERY_DEGRADATION) / 60.0

        # Battery voltage drop: -0.1V per 5 minutes
        voltage_drop = (elapsed_minutes / 5.0) * 0.1
        telemetry.battery_voltage = max(0.0, 13.8 - voltage_drop)

        return telemetry

    def _apply_fuel_leak(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply fuel leak scenario.
        """
        elapsed_minutes = self.get_time_since_activation(FailureScenario.FUEL_LEAK) / 60.0

        # Fuel leak: 5% per minute
        leak_amount = elapsed_minutes * 5.0
        telemetry.fuel_level_percent = max(0.0, 75.0 - leak_amount)

        return telemetry
