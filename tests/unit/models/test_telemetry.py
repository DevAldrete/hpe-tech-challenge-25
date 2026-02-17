"""
Unit tests for telemetry.py models.

Tests cover VehicleTelemetry model.
"""

import pytest
from pydantic import ValidationError

from src.models.telemetry import VehicleTelemetry


@pytest.mark.unit
@pytest.mark.models
class TestVehicleTelemetry:
    """Test VehicleTelemetry model validation and behavior."""

    def test_vehicle_telemetry_valid_creation(self, sample_telemetry_data: dict) -> None:
        """Test creating a valid VehicleTelemetry instance."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert telemetry.vehicle_id == "AMB-001"
        assert telemetry.sequence_number == 12345
        assert telemetry.odometer_km == 45678.9
        assert telemetry.engine_temp_celsius == 92.5
        assert telemetry.engine_rpm == 2500
        assert telemetry.battery_voltage == 13.8
        assert telemetry.fuel_level_percent == 75.0

    def test_vehicle_telemetry_location_embedded(self, sample_telemetry_data: dict) -> None:
        """Test telemetry contains embedded GeoLocation."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert telemetry.location.latitude == 37.7749
        assert telemetry.location.longitude == -122.4194
        assert telemetry.location.speed_kmh == 65.5

    def test_vehicle_telemetry_engine_temp_bounds(self, sample_telemetry_data: dict) -> None:
        """Test engine_temp_celsius enforces -40 to 150 range."""
        sample_telemetry_data["engine_temp_celsius"] = 151.0
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

        sample_telemetry_data["engine_temp_celsius"] = -41.0
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

    def test_vehicle_telemetry_engine_rpm_bounds(self, sample_telemetry_data: dict) -> None:
        """Test engine_rpm enforces 0 to 8000 range."""
        sample_telemetry_data["engine_rpm"] = -1
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

        sample_telemetry_data["engine_rpm"] = 8001
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

    def test_vehicle_telemetry_battery_voltage_bounds(self, sample_telemetry_data: dict) -> None:
        """Test battery_voltage enforces 0 to 30 range."""
        sample_telemetry_data["battery_voltage"] = -0.1
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

        sample_telemetry_data["battery_voltage"] = 30.1
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

    def test_vehicle_telemetry_fuel_level_percent_bounds(self, sample_telemetry_data: dict) -> None:
        """Test fuel_level_percent enforces 0 to 100 range."""
        sample_telemetry_data["fuel_level_percent"] = -1.0
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

        sample_telemetry_data["fuel_level_percent"] = 101.0
        with pytest.raises(ValidationError):
            VehicleTelemetry(**sample_telemetry_data)

    def test_vehicle_telemetry_brake_pad_thickness(self, sample_telemetry_data: dict) -> None:
        """Test brake_pad_thickness_mm has all four wheels."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert "front_left" in telemetry.brake_pad_thickness_mm
        assert "front_right" in telemetry.brake_pad_thickness_mm
        assert "rear_left" in telemetry.brake_pad_thickness_mm
        assert "rear_right" in telemetry.brake_pad_thickness_mm

    def test_vehicle_telemetry_tire_pressure(self, sample_telemetry_data: dict) -> None:
        """Test tire_pressure_psi has all four wheels."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert "front_left" in telemetry.tire_pressure_psi
        assert "front_right" in telemetry.tire_pressure_psi
        assert "rear_left" in telemetry.tire_pressure_psi
        assert "rear_right" in telemetry.tire_pressure_psi

    def test_vehicle_telemetry_vibration_g_force(self, sample_telemetry_data: dict) -> None:
        """Test vibration_g_force has x, y, z axes."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert "x" in telemetry.vibration_g_force
        assert "y" in telemetry.vibration_g_force
        assert "z" in telemetry.vibration_g_force

    def test_vehicle_telemetry_emergency_equipment_status(
        self, sample_telemetry_data: dict
    ) -> None:
        """Test emergency equipment fields."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert telemetry.siren_active is True
        assert telemetry.lights_active is True

    def test_vehicle_telemetry_active_dtc_codes_default(self, sample_telemetry_data: dict) -> None:
        """Test active_dtc_codes defaults to empty list."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert telemetry.active_dtc_codes == []

    def test_vehicle_telemetry_with_dtc_codes(self, sample_telemetry_data: dict) -> None:
        """Test telemetry can include diagnostic trouble codes."""
        sample_telemetry_data["active_dtc_codes"] = ["P0420", "P0171"]
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        assert len(telemetry.active_dtc_codes) == 2
        assert "P0420" in telemetry.active_dtc_codes

    def test_vehicle_telemetry_serialization(self, sample_telemetry_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        telemetry = VehicleTelemetry(**sample_telemetry_data)
        json_data = telemetry.model_dump()

        assert json_data["vehicle_id"] == "AMB-001"
        assert json_data["sequence_number"] == 12345

        # Test round-trip
        telemetry_from_json = VehicleTelemetry(**json_data)
        assert telemetry_from_json.vehicle_id == telemetry.vehicle_id
        assert telemetry_from_json.engine_rpm == telemetry.engine_rpm

    def test_vehicle_telemetry_required_fields(self, sample_datetime) -> None:
        """Test that required fields cannot be omitted."""
        with pytest.raises(ValidationError) as exc_info:
            VehicleTelemetry(
                vehicle_id="AMB-001",
                timestamp=sample_datetime,
                # Missing many required fields
            )
        error_str = str(exc_info.value)
        assert "sequence_number" in error_str
        assert "location" in error_str
