"""
Anomaly detection system for vehicle telemetry.

Uses rule-based thresholds to detect failures and generate predictive alerts.
"""

from datetime import datetime

from src.models.alerts import PredictiveAlert
from src.models.enums import AlertSeverity, FailureCategory
from src.models.telemetry import VehicleTelemetry


class AnomalyDetector:
    """Rule-based anomaly detection for vehicle telemetry."""

    def __init__(self, vehicle_id: str) -> None:
        """
        Initialize the anomaly detector.

        Args:
            vehicle_id: Unique identifier for the vehicle
        """
        self.vehicle_id = vehicle_id

    def analyze(self, telemetry: VehicleTelemetry) -> list[PredictiveAlert]:
        """
        Analyze telemetry and generate alerts for anomalies.

        Args:
            telemetry: Current vehicle telemetry data

        Returns:
            List of predictive alerts (may be empty)
        """
        alerts: list[PredictiveAlert] = []

        # Check all failure conditions
        alerts.extend(self._check_engine_temp(telemetry))
        alerts.extend(self._check_alternator(telemetry))
        alerts.extend(self._check_battery(telemetry))
        alerts.extend(self._check_brake_pads(telemetry))
        alerts.extend(self._check_tire_pressure(telemetry))

        return alerts

    def _check_engine_temp(self, telemetry: VehicleTelemetry) -> list[PredictiveAlert]:
        """
        Check engine temperature for overheating.

        Thresholds from SIMULATION.md:
        - WARNING: > 105°C
        - CRITICAL: > 120°C
        """
        alerts: list[PredictiveAlert] = []
        temp = telemetry.engine_temp_celsius

        if temp > 120.0:
            alerts.append(
                PredictiveAlert(
                    vehicle_id=self.vehicle_id,
                    timestamp=datetime.utcnow(),
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
                    recommended_action="STOP IMMEDIATELY - Engine damage imminent. Activate limp mode.",
                    contributing_factors=[
                        f"engine_temp_celsius={temp:.1f}°C (critical threshold 120°C)",
                        f"coolant_temp={telemetry.coolant_temp_celsius:.1f}°C",
                        f"rpm={telemetry.engine_rpm}",
                    ],
                    related_telemetry={
                        "engine_temp_celsius": temp,
                        "coolant_temp_celsius": telemetry.coolant_temp_celsius,
                        "engine_rpm": telemetry.engine_rpm,
                    },
                )
            )
        elif temp > 105.0:
            alerts.append(
                PredictiveAlert(
                    vehicle_id=self.vehicle_id,
                    timestamp=datetime.utcnow(),
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
                    recommended_action="Reduce RPM and monitor temperature. Schedule inspection within 4 hours.",
                    contributing_factors=[
                        f"engine_temp_celsius={temp:.1f}°C (warning threshold 105°C)",
                        f"coolant_temp={telemetry.coolant_temp_celsius:.1f}°C",
                    ],
                    related_telemetry={
                        "engine_temp_celsius": temp,
                        "coolant_temp_celsius": telemetry.coolant_temp_celsius,
                    },
                )
            )

        return alerts

    def _check_alternator(self, telemetry: VehicleTelemetry) -> list[PredictiveAlert]:
        """
        Check alternator output voltage.

        Thresholds from SIMULATION.md:
        - WARNING: < 13.5V (not charging properly)
        - CRITICAL: < 13.0V (battery discharging)
        """
        alerts: list[PredictiveAlert] = []
        voltage = telemetry.alternator_voltage

        if voltage < 13.0:
            alerts.append(
                PredictiveAlert(
                    vehicle_id=self.vehicle_id,
                    timestamp=datetime.utcnow(),
                    severity=AlertSeverity.CRITICAL,
                    category=FailureCategory.ELECTRICAL,
                    component="alternator",
                    failure_probability=0.85,
                    confidence=0.90,
                    predicted_failure_min_hours=1.0,
                    predicted_failure_max_hours=4.0,
                    predicted_failure_likely_hours=2.0,
                    can_complete_current_mission=True,
                    safe_to_operate=True,
                    recommended_action="Alternator not charging - Battery will drain. Replace alternator within 2 hours.",
                    contributing_factors=[
                        f"alternator_voltage={voltage:.2f}V (critical threshold 13.0V)",
                        f"battery_soc={telemetry.battery_state_of_charge_percent:.1f}%",
                        f"battery_voltage={telemetry.battery_voltage:.2f}V",
                    ],
                    related_telemetry={
                        "alternator_voltage": voltage,
                        "battery_state_of_charge_percent": telemetry.battery_state_of_charge_percent,
                        "battery_voltage": telemetry.battery_voltage,
                    },
                )
            )
        elif voltage < 13.5:
            alerts.append(
                PredictiveAlert(
                    vehicle_id=self.vehicle_id,
                    timestamp=datetime.utcnow(),
                    severity=AlertSeverity.WARNING,
                    category=FailureCategory.ELECTRICAL,
                    component="alternator",
                    failure_probability=0.65,
                    confidence=0.85,
                    predicted_failure_min_hours=8.0,
                    predicted_failure_max_hours=24.0,
                    predicted_failure_likely_hours=12.0,
                    can_complete_current_mission=True,
                    safe_to_operate=True,
                    recommended_action="Alternator output low - Schedule inspection within 12 hours.",
                    contributing_factors=[
                        f"alternator_voltage={voltage:.2f}V (warning threshold 13.5V)",
                        f"battery_soc={telemetry.battery_state_of_charge_percent:.1f}%",
                    ],
                    related_telemetry={
                        "alternator_voltage": voltage,
                        "battery_state_of_charge_percent": telemetry.battery_state_of_charge_percent,
                    },
                )
            )

        return alerts

    def _check_battery(self, telemetry: VehicleTelemetry) -> list[PredictiveAlert]:
        """
        Check battery state of charge.

        Thresholds from SIMULATION.md:
        - WARNING: < 40%
        - CRITICAL: < 20%
        """
        alerts: list[PredictiveAlert] = []
        soc = telemetry.battery_state_of_charge_percent

        if soc < 20.0:
            alerts.append(
                PredictiveAlert(
                    vehicle_id=self.vehicle_id,
                    timestamp=datetime.utcnow(),
                    severity=AlertSeverity.CRITICAL,
                    category=FailureCategory.ELECTRICAL,
                    component="battery",
                    failure_probability=0.90,
                    confidence=0.95,
                    predicted_failure_min_hours=0.5,
                    predicted_failure_max_hours=2.0,
                    predicted_failure_likely_hours=1.0,
                    can_complete_current_mission=False,
                    safe_to_operate=False,
                    recommended_action="Battery critically low - Vehicle may shut down. Return to base immediately.",
                    contributing_factors=[
                        f"battery_soc={soc:.1f}% (critical threshold 20%)",
                        f"battery_voltage={telemetry.battery_voltage:.2f}V",
                        f"alternator_voltage={telemetry.alternator_voltage:.2f}V",
                    ],
                    related_telemetry={
                        "battery_state_of_charge_percent": soc,
                        "battery_voltage": telemetry.battery_voltage,
                        "alternator_voltage": telemetry.alternator_voltage,
                    },
                )
            )
        elif soc < 40.0:
            alerts.append(
                PredictiveAlert(
                    vehicle_id=self.vehicle_id,
                    timestamp=datetime.utcnow(),
                    severity=AlertSeverity.WARNING,
                    category=FailureCategory.ELECTRICAL,
                    component="battery",
                    failure_probability=0.50,
                    confidence=0.80,
                    predicted_failure_min_hours=2.0,
                    predicted_failure_max_hours=6.0,
                    predicted_failure_likely_hours=4.0,
                    can_complete_current_mission=True,
                    safe_to_operate=True,
                    recommended_action="Battery charge low - Check charging system and battery health.",
                    contributing_factors=[
                        f"battery_soc={soc:.1f}% (warning threshold 40%)",
                        f"alternator_voltage={telemetry.alternator_voltage:.2f}V",
                    ],
                    related_telemetry={
                        "battery_state_of_charge_percent": soc,
                        "battery_voltage": telemetry.battery_voltage,
                        "alternator_voltage": telemetry.alternator_voltage,
                    },
                )
            )

        return alerts

    def _check_brake_pads(self, telemetry: VehicleTelemetry) -> list[PredictiveAlert]:
        """
        Check brake pad thickness.

        Thresholds from SIMULATION.md:
        - WARNING: < 3.0mm
        - CRITICAL: < 1.5mm
        """
        alerts: list[PredictiveAlert] = []

        # Check all four brake pads
        for location, thickness in telemetry.brake_pad_thickness_mm.items():
            if thickness < 1.5:
                alerts.append(
                    PredictiveAlert(
                        vehicle_id=self.vehicle_id,
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.CRITICAL,
                        category=FailureCategory.BRAKES,
                        component=f"brake_pad_{location}",
                        failure_probability=0.95,
                        confidence=0.98,
                        predicted_failure_min_hours=0.0,
                        predicted_failure_max_hours=1.0,
                        predicted_failure_likely_hours=0.5,
                        can_complete_current_mission=False,
                        safe_to_operate=False,
                        recommended_action=f"CRITICAL: {location} brake pad at {thickness:.1f}mm - Replace immediately (metal-on-metal imminent).",
                        contributing_factors=[
                            f"brake_pad_{location}={thickness:.1f}mm (critical threshold 1.5mm)"
                        ],
                        related_telemetry={
                            f"brake_pad_{location}_mm": thickness,
                        },
                    )
                )
            elif thickness < 3.0:
                alerts.append(
                    PredictiveAlert(
                        vehicle_id=self.vehicle_id,
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.WARNING,
                        category=FailureCategory.BRAKES,
                        component=f"brake_pad_{location}",
                        failure_probability=0.60,
                        confidence=0.90,
                        predicted_failure_min_hours=24.0,
                        predicted_failure_max_hours=72.0,
                        predicted_failure_likely_hours=48.0,
                        can_complete_current_mission=True,
                        safe_to_operate=True,
                        recommended_action=f"{location} brake pad at {thickness:.1f}mm - Schedule replacement within 48 hours.",
                        contributing_factors=[
                            f"brake_pad_{location}={thickness:.1f}mm (warning threshold 3.0mm)"
                        ],
                        related_telemetry={f"brake_pad_{location}_mm": thickness},
                    )
                )

        return alerts

    def _check_tire_pressure(
        self, telemetry: VehicleTelemetry
    ) -> list[PredictiveAlert]:
        """
        Check tire pressures.

        Thresholds from SIMULATION.md:
        - WARNING: < 60 psi
        - CRITICAL: < 40 psi
        """
        alerts: list[PredictiveAlert] = []

        # Check all four tires
        for location, pressure in telemetry.tire_pressure_psi.items():
            if pressure < 40.0:
                alerts.append(
                    PredictiveAlert(
                        vehicle_id=self.vehicle_id,
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.CRITICAL,
                        category=FailureCategory.TIRES,
                        component=f"tire_{location}",
                        failure_probability=0.90,
                        confidence=0.95,
                        predicted_failure_min_hours=0.0,
                        predicted_failure_max_hours=0.5,
                        predicted_failure_likely_hours=0.25,
                        can_complete_current_mission=False,
                        safe_to_operate=False,
                        recommended_action=f"CRITICAL: {location} tire at {pressure:.1f} psi - Stop and replace immediately.",
                        contributing_factors=[
                            f"tire_pressure_{location}={pressure:.1f} psi (critical threshold 40 psi)"
                        ],
                        related_telemetry={
                            f"tire_pressure_{location}_psi": pressure,
                        },
                    )
                )
            elif pressure < 60.0:
                alerts.append(
                    PredictiveAlert(
                        vehicle_id=self.vehicle_id,
                        timestamp=datetime.utcnow(),
                        severity=AlertSeverity.WARNING,
                        category=FailureCategory.TIRES,
                        component=f"tire_{location}",
                        failure_probability=0.50,
                        confidence=0.85,
                        predicted_failure_min_hours=1.0,
                        predicted_failure_max_hours=4.0,
                        predicted_failure_likely_hours=2.0,
                        can_complete_current_mission=True,
                        safe_to_operate=True,
                        recommended_action=f"{location} tire pressure low at {pressure:.1f} psi - Inspect for leak and refill.",
                        contributing_factors=[
                            f"tire_pressure_{location}={pressure:.1f} psi (warning threshold 60 psi)"
                        ],
                        related_telemetry={f"tire_pressure_{location}_psi": pressure},
                    )
                )

        return alerts
