"""
Unit tests for enums.py.

Tests cover all enum types used in Project AEGIS.
"""

import pytest

from src.models.enums import (
    AlertSeverity,
    CommandType,
    FailureCategory,
    FailureScenario,
    MaintenanceUrgency,
    MessagePriority,
    MessageType,
    OperationalStatus,
    VehicleType,
)


@pytest.mark.unit
@pytest.mark.models
class TestVehicleType:
    """Test VehicleType enum."""

    def test_vehicle_type_values(self) -> None:
        """Test VehicleType has expected values."""
        assert VehicleType.AMBULANCE.value == "ambulance"
        assert VehicleType.FIRE_TRUCK.value == "fire_truck"

    def test_vehicle_type_membership(self) -> None:
        """Test VehicleType membership checks."""
        assert "ambulance" in [vt.value for vt in VehicleType]
        assert "fire_truck" in [vt.value for vt in VehicleType]

    def test_vehicle_type_count(self) -> None:
        """Test VehicleType has expected number of members."""
        assert len(VehicleType) == 2


@pytest.mark.unit
@pytest.mark.models
class TestOperationalStatus:
    """Test OperationalStatus enum."""

    def test_operational_status_values(self) -> None:
        """Test OperationalStatus has expected values."""
        assert OperationalStatus.IDLE.value == "idle"
        assert OperationalStatus.EN_ROUTE.value == "en_route"
        assert OperationalStatus.ON_SCENE.value == "on_scene"
        assert OperationalStatus.RETURNING.value == "returning"
        assert OperationalStatus.MAINTENANCE.value == "maintenance"
        assert OperationalStatus.OUT_OF_SERVICE.value == "out_of_service"
        assert OperationalStatus.OFFLINE.value == "offline"

    def test_operational_status_count(self) -> None:
        """Test OperationalStatus has expected number of members."""
        assert len(OperationalStatus) == 7


@pytest.mark.unit
@pytest.mark.models
class TestAlertSeverity:
    """Test AlertSeverity enum."""

    def test_alert_severity_values(self) -> None:
        """Test AlertSeverity has expected values."""
        assert AlertSeverity.CRITICAL.value == "critical"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.INFO.value == "info"

    def test_alert_severity_count(self) -> None:
        """Test AlertSeverity has expected number of members."""
        assert len(AlertSeverity) == 3


@pytest.mark.unit
@pytest.mark.models
class TestFailureCategory:
    """Test FailureCategory enum."""

    def test_failure_category_values(self) -> None:
        """Test FailureCategory has expected critical values."""
        assert FailureCategory.ENGINE.value == "engine"
        assert FailureCategory.TRANSMISSION.value == "transmission"
        assert FailureCategory.ELECTRICAL.value == "electrical"
        assert FailureCategory.BRAKES.value == "brakes"
        assert FailureCategory.COOLING.value == "cooling"
        assert FailureCategory.FUEL.value == "fuel"
        assert FailureCategory.TIRES.value == "tires"
        assert FailureCategory.SUSPENSION.value == "suspension"
        assert FailureCategory.EQUIPMENT.value == "equipment"

    def test_failure_category_count(self) -> None:
        """Test FailureCategory has expected number of members."""
        assert len(FailureCategory) == 9


@pytest.mark.unit
@pytest.mark.models
class TestMaintenanceUrgency:
    """Test MaintenanceUrgency enum."""

    def test_maintenance_urgency_values(self) -> None:
        """Test MaintenanceUrgency has expected values."""
        assert MaintenanceUrgency.IMMEDIATE.value == "immediate"
        assert MaintenanceUrgency.URGENT.value == "urgent"
        assert MaintenanceUrgency.SCHEDULED.value == "scheduled"
        assert MaintenanceUrgency.PREVENTIVE.value == "preventive"

    def test_maintenance_urgency_count(self) -> None:
        """Test MaintenanceUrgency has expected number of members."""
        assert len(MaintenanceUrgency) == 4


@pytest.mark.unit
@pytest.mark.models
class TestMessageType:
    """Test MessageType enum."""

    def test_message_type_vehicle_to_orchestrator(self) -> None:
        """Test vehicle to orchestrator message types."""
        assert MessageType.TELEMETRY_UPDATE.value == "telemetry.update"
        assert MessageType.HEARTBEAT.value == "vehicle.heartbeat"
        assert MessageType.ALERT_GENERATED.value == "alert.generated"
        assert MessageType.STATUS_CHANGE.value == "vehicle.status_change"
        assert MessageType.LOCAL_DECISION.value == "vehicle.local_decision"

    def test_message_type_orchestrator_to_vehicle(self) -> None:
        """Test orchestrator to vehicle message types."""
        assert MessageType.COMMAND.value == "vehicle.command"
        assert MessageType.CONFIG_UPDATE.value == "vehicle.config_update"
        assert MessageType.ALERT_ACKNOWLEDGE.value == "alert.acknowledge"
        assert MessageType.MISSION_ASSIGNMENT.value == "mission.assignment"
        assert MessageType.OVERRIDE_DECISION.value == "vehicle.override"

    def test_message_type_orchestrator_to_dashboard(self) -> None:
        """Test orchestrator to dashboard message types."""
        assert MessageType.FLEET_STATUS.value == "fleet.status"
        assert MessageType.ALERT_BROADCAST.value == "alert.broadcast"
        assert MessageType.VEHICLE_UPDATE.value == "vehicle.update"


@pytest.mark.unit
@pytest.mark.models
class TestMessagePriority:
    """Test MessagePriority enum."""

    def test_message_priority_values(self) -> None:
        """Test MessagePriority has expected values."""
        assert MessagePriority.CRITICAL.value == "critical"
        assert MessagePriority.HIGH.value == "high"
        assert MessagePriority.NORMAL.value == "normal"
        assert MessagePriority.LOW.value == "low"

    def test_message_priority_count(self) -> None:
        """Test MessagePriority has expected number of members."""
        assert len(MessagePriority) == 4


@pytest.mark.unit
@pytest.mark.models
class TestCommandType:
    """Test CommandType enum."""

    def test_command_type_values(self) -> None:
        """Test CommandType has expected values."""
        assert CommandType.STANDBY.value == "standby"
        assert CommandType.DISPATCH.value == "dispatch"
        assert CommandType.RETURN_TO_BASE.value == "return_to_base"
        assert CommandType.MAINTENANCE_MODE.value == "maintenance_mode"
        assert CommandType.EMERGENCY_STOP.value == "emergency_stop"
        assert CommandType.UPDATE_CONFIG.value == "update_config"

    def test_command_type_count(self) -> None:
        """Test CommandType has expected number of members."""
        assert len(CommandType) == 6


@pytest.mark.unit
@pytest.mark.models
class TestFailureScenario:
    """Test FailureScenario enum."""

    def test_failure_scenario_engine_failures(self) -> None:
        """Test engine failure scenarios."""
        assert FailureScenario.ENGINE_OVERHEAT.value == "engine_overheat"
        assert FailureScenario.OIL_PRESSURE_DROP.value == "oil_pressure_drop"
        assert FailureScenario.COOLANT_LEAK.value == "coolant_leak"

    def test_failure_scenario_electrical_failures(self) -> None:
        """Test electrical failure scenarios."""
        assert FailureScenario.ALTERNATOR_FAILURE.value == "alternator_failure"
        assert FailureScenario.BATTERY_DEGRADATION.value == "battery_degradation"
        assert FailureScenario.VOLTAGE_SPIKE.value == "voltage_spike"

    def test_failure_scenario_brake_failures(self) -> None:
        """Test brake failure scenarios."""
        assert FailureScenario.BRAKE_PAD_WEAR_CRITICAL.value == "brake_pad_wear_critical"
        assert FailureScenario.BRAKE_FLUID_LEAK.value == "brake_fluid_leak"
        assert FailureScenario.ABS_MALFUNCTION.value == "abs_malfunction"

    def test_failure_scenario_tire_failures(self) -> None:
        """Test tire failure scenarios."""
        assert FailureScenario.TIRE_PRESSURE_LOW.value == "tire_pressure_low"
        assert FailureScenario.TIRE_BLOWOUT.value == "tire_blowout"
        assert FailureScenario.UNEVEN_TIRE_WEAR.value == "uneven_tire_wear"

    def test_failure_scenario_fuel_system(self) -> None:
        """Test fuel system failure scenarios."""
        assert FailureScenario.FUEL_PUMP_FAILURE.value == "fuel_pump_failure"
        assert FailureScenario.FUEL_LEAK.value == "fuel_leak"
        assert FailureScenario.INJECTOR_CLOG.value == "injector_clog"

    def test_failure_scenario_transmission(self) -> None:
        """Test transmission failure scenarios."""
        assert FailureScenario.TRANSMISSION_OVERHEAT.value == "transmission_overheat"
        assert FailureScenario.GEAR_SLIPPAGE.value == "gear_slippage"

    def test_failure_scenario_equipment(self) -> None:
        """Test equipment failure scenarios."""
        assert FailureScenario.WATER_PUMP_FAILURE.value == "water_pump_failure"
        assert FailureScenario.LADDER_HYDRAULIC_LEAK.value == "ladder_hydraulic_leak"
        assert FailureScenario.DEFIBRILLATOR_BATTERY_LOW.value == "defibrillator_battery_low"
        assert FailureScenario.MEDICAL_OXYGEN_LOW.value == "medical_oxygen_low"

    def test_failure_scenario_count(self) -> None:
        """Test FailureScenario has expected minimum number of members."""
        # Should have at least 20 different failure scenarios
        assert len(FailureScenario) >= 20
