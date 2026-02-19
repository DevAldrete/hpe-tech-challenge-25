"""
Failure injection system for vehicle simulation.

Modifies telemetry based on active failure scenarios to simulate realistic degradation.
"""

from datetime import datetime

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
        self.active_scenarios[scenario] = datetime.utcnow()

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
        elapsed = datetime.utcnow() - self.active_scenarios[scenario]
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
            elif scenario == FailureScenario.ALTERNATOR_FAILURE:
                modified = self._apply_alternator_failure(modified)
            elif scenario == FailureScenario.BRAKE_PAD_WEAR_CRITICAL:
                modified = self._apply_brake_pad_wear(modified)
            elif scenario == FailureScenario.TIRE_PRESSURE_LOW:
                modified = self._apply_tire_leak(modified)

        return modified

    def _apply_engine_overheat(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply engine overheat scenario.

        Progression: Temperature rise (simulating coolant leak effect)
        - Engine temp: +2°C per minute
        - Coolant temp: +2.5°C per minute

        Timeline from SIMULATION.md:
        - t=0: Normal (engine_temp=90°C)
        - t=5min: Leak starts
        - t=15min: 105°C (WARNING threshold)
        - t=25min: 120°C (CRITICAL threshold)
        """
        elapsed_minutes = self.get_time_since_activation(FailureScenario.ENGINE_OVERHEAT) / 60.0

        # Temperature rise: +2°C per minute from baseline
        temp_increase = elapsed_minutes * 2.0
        telemetry.engine_temp_celsius = min(90.0 + temp_increase, 150.0)
        telemetry.coolant_temp_celsius = min(85.0 + elapsed_minutes * 2.5, 150.0)

        return telemetry

    def _apply_alternator_failure(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply alternator failure scenario.

        Progression: Gradual voltage decline + battery discharge
        - Alternator voltage: -0.1V per 5 minutes
        - Battery SOC: -3% per minute (discharging)

        Timeline from SIMULATION.md:
        - t=0: Normal (14.2V)
        - t=20min: 13.8V
        - t=40min: 13.2V (WARNING: not charging)
        - t=60min: 12.8V (battery discharging)
        """
        elapsed_minutes = self.get_time_since_activation(FailureScenario.ALTERNATOR_FAILURE) / 60.0

        # Alternator voltage decline: -0.1V per 5 minutes
        voltage_drop = (elapsed_minutes / 5.0) * 0.1
        telemetry.alternator_voltage = max(11.5, 14.2 - voltage_drop)

        # Battery discharging: -3% per minute
        battery_loss = elapsed_minutes * 3.0
        telemetry.battery_state_of_charge_percent = max(0.0, 100.0 - battery_loss)

        # Battery voltage correlates with SOC
        telemetry.battery_voltage = 11.5 + (telemetry.battery_state_of_charge_percent / 100.0) * 2.5

        return telemetry

    def _apply_brake_pad_wear(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply brake pad wear scenario.

        Progression: Gradual pad thickness reduction
        - Initial: 8.0mm (front), 9.0mm (rear)
        - Wear rate: 0.05mm per minute (simulated heavy use)
        - WARNING threshold: 3.0mm
        - CRITICAL threshold: 1.5mm

        Timeline from SIMULATION.md:
        - t=0: 8mm (normal)
        - t=100 minutes: 3.5mm (WARNING range)
        - t=110 minutes: 2.5mm (CRITICAL range)
        """
        elapsed_minutes = (
            self.get_time_since_activation(FailureScenario.BRAKE_PAD_WEAR_CRITICAL) / 60.0
        )

        # Wear: 0.05mm per minute
        wear_amount = elapsed_minutes * 0.05

        # Front pads wear 30% faster (from docs)
        front_wear = wear_amount * 1.3
        rear_wear = wear_amount

        telemetry.brake_pad_thickness_mm["front_left"] = max(0.0, 8.0 - front_wear)
        telemetry.brake_pad_thickness_mm["front_right"] = max(0.0, 8.0 - front_wear)
        telemetry.brake_pad_thickness_mm["rear_left"] = max(0.0, 9.0 - rear_wear)
        telemetry.brake_pad_thickness_mm["rear_right"] = max(0.0, 9.0 - rear_wear)

        # Brake temperature increases with wear (all wheels)
        base_temp = 40.0 + elapsed_minutes * 0.5
        for wheel in ["front_left", "front_right", "rear_left", "rear_right"]:
            telemetry.brake_temp_celsius[wheel] = min(base_temp, 120.0)

        return telemetry

    def _apply_tire_leak(self, telemetry: VehicleTelemetry) -> VehicleTelemetry:
        """
        Apply tire pressure leak scenario.

        Progression: Slow leak in front_left tire
        - Initial: 80 psi
        - Leak rate: 2 psi per minute
        - WARNING threshold: 60 psi
        - CRITICAL threshold: 40 psi

        Timeline from SIMULATION.md:
        - t=0: 80 psi (normal)
        - t=10min: 60 psi (WARNING)
        - t=20min: 40 psi (CRITICAL)
        """
        elapsed_minutes = self.get_time_since_activation(FailureScenario.TIRE_PRESSURE_LOW) / 60.0

        # Pressure loss: 2 psi per minute
        pressure_loss = elapsed_minutes * 2.0
        telemetry.tire_pressure_psi["front_left"] = max(0.0, 80.0 - pressure_loss)

        # Vibration increases as tire deflates (z-axis primarily)
        vibration_increase = min(elapsed_minutes * 0.02, 0.5)
        telemetry.vibration_g_force["z"] = (
            telemetry.vibration_g_force.get("z", 0.0) + vibration_increase
        )

        return telemetry
