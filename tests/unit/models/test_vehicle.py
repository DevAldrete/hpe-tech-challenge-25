"""
Unit tests for vehicle.py models.

Tests cover GeoLocation, VehicleIdentity, and VehicleState models.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.enums import OperationalStatus, VehicleType
from src.models.vehicle import GeoLocation, VehicleIdentity, VehicleState


@pytest.mark.unit
@pytest.mark.models
class TestGeoLocation:
    """Test GeoLocation model validation and behavior."""

    def test_geolocation_valid_creation(self, sample_geolocation_data: dict) -> None:
        """Test creating a valid GeoLocation instance."""
        location = GeoLocation(**sample_geolocation_data)
        assert location.latitude == 37.7749
        assert location.longitude == -122.4194
        assert location.altitude == 15.5
        assert location.accuracy == 5.0
        assert location.heading == 45.0
        assert location.speed_kmh == 65.5

    def test_geolocation_latitude_bounds(self, sample_geolocation_data: dict) -> None:
        """Test latitude validation enforces -90 to 90 range."""
        # Test upper bound
        sample_geolocation_data["latitude"] = 91.0
        with pytest.raises(ValidationError) as exc_info:
            GeoLocation(**sample_geolocation_data)
        assert "latitude" in str(exc_info.value)

        # Test lower bound
        sample_geolocation_data["latitude"] = -91.0
        with pytest.raises(ValidationError):
            GeoLocation(**sample_geolocation_data)

        # Test valid boundaries
        sample_geolocation_data["latitude"] = 90.0
        location = GeoLocation(**sample_geolocation_data)
        assert location.latitude == 90.0

        sample_geolocation_data["latitude"] = -90.0
        location = GeoLocation(**sample_geolocation_data)
        assert location.latitude == -90.0

    def test_geolocation_longitude_bounds(self, sample_geolocation_data: dict) -> None:
        """Test longitude validation enforces -180 to 180 range."""
        # Test upper bound
        sample_geolocation_data["longitude"] = 181.0
        with pytest.raises(ValidationError) as exc_info:
            GeoLocation(**sample_geolocation_data)
        assert "longitude" in str(exc_info.value)

        # Test lower bound
        sample_geolocation_data["longitude"] = -181.0
        with pytest.raises(ValidationError):
            GeoLocation(**sample_geolocation_data)

    def test_geolocation_heading_bounds(self, sample_geolocation_data: dict) -> None:
        """Test heading validation enforces 0 to 360 range."""
        sample_geolocation_data["heading"] = 361.0
        with pytest.raises(ValidationError):
            GeoLocation(**sample_geolocation_data)

        sample_geolocation_data["heading"] = -1.0
        with pytest.raises(ValidationError):
            GeoLocation(**sample_geolocation_data)

    def test_geolocation_speed_non_negative(self, sample_geolocation_data: dict) -> None:
        """Test speed must be non-negative."""
        sample_geolocation_data["speed_kmh"] = -10.0
        with pytest.raises(ValidationError):
            GeoLocation(**sample_geolocation_data)

        sample_geolocation_data["speed_kmh"] = 0.0
        location = GeoLocation(**sample_geolocation_data)
        assert location.speed_kmh == 0.0

    def test_geolocation_defaults(self) -> None:
        """Test default values for optional fields."""
        location = GeoLocation(
            latitude=0.0,
            longitude=0.0,
            timestamp=datetime.now(timezone.utc),
        )
        assert location.altitude == 0.0
        assert location.accuracy == 10.0
        assert location.heading == 0.0
        assert location.speed_kmh == 0.0

    def test_geolocation_serialization(self, sample_geolocation_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        location = GeoLocation(**sample_geolocation_data)
        json_data = location.model_dump()

        assert json_data["latitude"] == 37.7749
        assert json_data["longitude"] == -122.4194

        # Test round-trip
        location_from_json = GeoLocation(**json_data)
        assert location_from_json.latitude == location.latitude
        assert location_from_json.longitude == location.longitude


@pytest.mark.unit
@pytest.mark.models
class TestVehicleIdentity:
    """Test VehicleIdentity model validation and behavior."""

    def test_vehicle_identity_valid_creation(self, sample_vehicle_identity_data: dict) -> None:
        """Test creating a valid VehicleIdentity instance."""
        vehicle = VehicleIdentity(**sample_vehicle_identity_data)
        assert vehicle.vehicle_id == "AMB-001"
        assert vehicle.vehicle_type == VehicleType.AMBULANCE
        assert vehicle.unit_number == "A1"
        assert vehicle.station_id == "ST-CENTRAL"
        assert vehicle.make == "Ford"
        assert vehicle.model == "F-450 Super Duty"
        assert vehicle.year == 2025
        assert vehicle.vin == "1FDUF5HT5MEC12345"
        assert "defibrillator" in vehicle.equipment_manifest

    def test_vehicle_identity_year_bounds(self, sample_vehicle_identity_data: dict) -> None:
        """Test year validation enforces 2000-2030 range."""
        sample_vehicle_identity_data["year"] = 1999
        with pytest.raises(ValidationError):
            VehicleIdentity(**sample_vehicle_identity_data)

        sample_vehicle_identity_data["year"] = 2031
        with pytest.raises(ValidationError):
            VehicleIdentity(**sample_vehicle_identity_data)

        # Test valid boundaries
        sample_vehicle_identity_data["year"] = 2000
        vehicle = VehicleIdentity(**sample_vehicle_identity_data)
        assert vehicle.year == 2000

        sample_vehicle_identity_data["year"] = 2030
        vehicle = VehicleIdentity(**sample_vehicle_identity_data)
        assert vehicle.year == 2030

    def test_vehicle_identity_vehicle_type_enum(self, sample_vehicle_identity_data: dict) -> None:
        """Test vehicle_type must be valid VehicleType enum."""
        sample_vehicle_identity_data["vehicle_type"] = VehicleType.FIRE_TRUCK
        vehicle = VehicleIdentity(**sample_vehicle_identity_data)
        assert vehicle.vehicle_type == VehicleType.FIRE_TRUCK

        # Invalid type should raise error
        sample_vehicle_identity_data["vehicle_type"] = "invalid_type"
        with pytest.raises(ValidationError):
            VehicleIdentity(**sample_vehicle_identity_data)

    def test_vehicle_identity_equipment_manifest_optional(
        self, sample_vehicle_identity_data: dict
    ) -> None:
        """Test equipment_manifest is optional with default empty dict."""
        del sample_vehicle_identity_data["equipment_manifest"]
        vehicle = VehicleIdentity(**sample_vehicle_identity_data)
        assert vehicle.equipment_manifest == {}

    def test_vehicle_identity_serialization(self, sample_vehicle_identity_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        vehicle = VehicleIdentity(**sample_vehicle_identity_data)
        json_data = vehicle.model_dump()

        assert json_data["vehicle_id"] == "AMB-001"
        assert json_data["vehicle_type"] == "ambulance"

        # Test round-trip
        vehicle_from_json = VehicleIdentity(**json_data)
        assert vehicle_from_json.vehicle_id == vehicle.vehicle_id
        assert vehicle_from_json.vin == vehicle.vin

    def test_vehicle_identity_required_fields(self) -> None:
        """Test that required fields cannot be omitted."""
        with pytest.raises(ValidationError) as exc_info:
            VehicleIdentity(
                vehicle_id="AMB-001",
                # Missing required fields
            )
        error_str = str(exc_info.value)
        assert "vehicle_type" in error_str
        assert "unit_number" in error_str
        assert "station_id" in error_str


@pytest.mark.unit
@pytest.mark.models
class TestVehicleState:
    """Test VehicleState model validation and behavior."""

    def test_vehicle_state_valid_creation(self, sample_vehicle_state_data: dict) -> None:
        """Test creating a valid VehicleState instance."""
        state = VehicleState(**sample_vehicle_state_data)
        assert state.vehicle_id == "AMB-001"
        assert state.operational_status == OperationalStatus.EN_ROUTE
        assert state.mission_id == "MISSION-2026-02-10-001"
        assert state.crew_count == 3
        assert len(state.assigned_crew) == 3
        assert state.eta_seconds == 420

    def test_vehicle_state_operational_status_enum(self, sample_vehicle_state_data: dict) -> None:
        """Test operational_status must be valid OperationalStatus enum."""
        for status in OperationalStatus:
            sample_vehicle_state_data["operational_status"] = status
            state = VehicleState(**sample_vehicle_state_data)
            assert state.operational_status == status

        # Invalid status should raise error
        sample_vehicle_state_data["operational_status"] = "invalid_status"
        with pytest.raises(ValidationError):
            VehicleState(**sample_vehicle_state_data)

    def test_vehicle_state_crew_count_non_negative(self, sample_vehicle_state_data: dict) -> None:
        """Test crew_count must be non-negative."""
        sample_vehicle_state_data["crew_count"] = -1
        with pytest.raises(ValidationError):
            VehicleState(**sample_vehicle_state_data)

        sample_vehicle_state_data["crew_count"] = 0
        state = VehicleState(**sample_vehicle_state_data)
        assert state.crew_count == 0

    def test_vehicle_state_eta_non_negative(self, sample_vehicle_state_data: dict) -> None:
        """Test eta_seconds must be non-negative when provided."""
        sample_vehicle_state_data["eta_seconds"] = -1
        with pytest.raises(ValidationError):
            VehicleState(**sample_vehicle_state_data)

        sample_vehicle_state_data["eta_seconds"] = 0
        state = VehicleState(**sample_vehicle_state_data)
        assert state.eta_seconds == 0

    def test_vehicle_state_optional_fields(
        self, sample_vehicle_state_data: dict, sample_datetime: datetime
    ) -> None:
        """Test optional fields can be None."""
        minimal_state_data = {
            "vehicle_id": "AMB-001",
            "timestamp": sample_datetime,
            "operational_status": OperationalStatus.IDLE,
        }
        state = VehicleState(**minimal_state_data)

        assert state.mission_id is None
        assert state.assigned_crew == []
        assert state.crew_count == 0
        assert state.destination is None
        assert state.eta_seconds is None

    def test_vehicle_state_with_destination(
        self, sample_vehicle_state_data: dict, sample_geolocation_data: dict
    ) -> None:
        """Test VehicleState can include GeoLocation destination."""
        sample_vehicle_state_data["destination"] = sample_geolocation_data
        state = VehicleState(**sample_vehicle_state_data)

        assert state.destination is not None
        assert state.destination.latitude == 37.7749
        assert state.destination.longitude == -122.4194

    def test_vehicle_state_serialization(self, sample_vehicle_state_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        state = VehicleState(**sample_vehicle_state_data)
        json_data = state.model_dump()

        assert json_data["vehicle_id"] == "AMB-001"
        assert json_data["operational_status"] == "en_route"

        # Test round-trip
        state_from_json = VehicleState(**json_data)
        assert state_from_json.vehicle_id == state.vehicle_id
        assert state_from_json.mission_id == state.mission_id
