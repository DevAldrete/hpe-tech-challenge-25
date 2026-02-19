"""
Unit tests for dispatch models in Project AEGIS.

Tests cover DispatchedUnit, Dispatch, and VehicleStatusSnapshot models.
"""

from datetime import datetime, timezone

import pytest

from src.models.dispatch import Dispatch, DispatchedUnit, VehicleStatusSnapshot
from src.models.enums import OperationalStatus, VehicleType
from src.models.vehicle import GeoLocation


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def sample_location() -> GeoLocation:
    """Provide a sample GeoLocation for dispatch tests."""
    return GeoLocation(
        latitude=19.4326,
        longitude=-99.1332,
        altitude=2240.0,
        accuracy=10.0,
        heading=0.0,
        speed_kmh=0.0,
        timestamp=datetime(2026, 2, 10, 14, 32, 1, tzinfo=timezone.utc),
    )


@pytest.fixture
def sample_dispatched_unit() -> DispatchedUnit:
    """Provide a sample DispatchedUnit."""
    return DispatchedUnit(
        vehicle_id="AMB-001",
        vehicle_type=VehicleType.AMBULANCE,
    )


@pytest.fixture
def sample_dispatch(sample_dispatched_unit: DispatchedUnit) -> Dispatch:
    """Provide a sample Dispatch with one unit."""
    return Dispatch(
        emergency_id="550e8400-e29b-41d4-a716-446655440000",
        units=[sample_dispatched_unit],
    )


@pytest.fixture
def sample_vehicle_snapshot(sample_location: GeoLocation) -> VehicleStatusSnapshot:
    """Provide a sample VehicleStatusSnapshot."""
    return VehicleStatusSnapshot(
        vehicle_id="AMB-001",
        vehicle_type=VehicleType.AMBULANCE,
        operational_status=OperationalStatus.IDLE,
        location=sample_location,
        battery_voltage=13.8,
        fuel_level_percent=75.0,
    )


# ---------------------------------------------------------------------------
# DispatchedUnit model
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.models
class TestDispatchedUnit:
    """Tests for DispatchedUnit model."""

    def test_valid_creation(self, sample_dispatched_unit: DispatchedUnit) -> None:
        """DispatchedUnit should be created with required fields."""
        assert sample_dispatched_unit.vehicle_id == "AMB-001"
        assert sample_dispatched_unit.vehicle_type == VehicleType.AMBULANCE

    def test_assigned_at_auto_set(self, sample_dispatched_unit: DispatchedUnit) -> None:
        """assigned_at should be set automatically."""
        assert sample_dispatched_unit.assigned_at is not None
        assert isinstance(sample_dispatched_unit.assigned_at, datetime)

    def test_default_not_acknowledged(self, sample_dispatched_unit: DispatchedUnit) -> None:
        """Default acknowledged state should be False."""
        assert sample_dispatched_unit.acknowledged is False

    def test_acknowledged_at_initially_none(self, sample_dispatched_unit: DispatchedUnit) -> None:
        """acknowledged_at should be None by default."""
        assert sample_dispatched_unit.acknowledged_at is None

    def test_acknowledgment_fields(self) -> None:
        """DispatchedUnit should accept acknowledgment data."""
        ts = datetime(2026, 2, 10, 14, 32, 10, tzinfo=timezone.utc)
        unit = DispatchedUnit(
            vehicle_id="FIRE-002",
            vehicle_type=VehicleType.FIRE_TRUCK,
            acknowledged=True,
            acknowledged_at=ts,
        )
        assert unit.acknowledged is True
        assert unit.acknowledged_at == ts


# ---------------------------------------------------------------------------
# Dispatch model
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.models
class TestDispatch:
    """Tests for Dispatch model."""

    def test_valid_creation(self, sample_dispatch: Dispatch) -> None:
        """Dispatch should be created with required fields."""
        assert sample_dispatch.emergency_id == "550e8400-e29b-41d4-a716-446655440000"
        assert len(sample_dispatch.units) == 1

    def test_dispatch_id_auto_generated(self, sample_dispatch: Dispatch) -> None:
        """dispatch_id should be auto-generated as a UUID string."""
        assert len(sample_dispatch.dispatch_id) == 36
        assert sample_dispatch.dispatch_id.count("-") == 4

    def test_dispatched_at_auto_set(self, sample_dispatch: Dispatch) -> None:
        """dispatched_at should be set automatically."""
        assert sample_dispatch.dispatched_at is not None
        assert isinstance(sample_dispatch.dispatched_at, datetime)

    def test_completed_at_initially_none(self, sample_dispatch: Dispatch) -> None:
        """completed_at should be None initially."""
        assert sample_dispatch.completed_at is None

    def test_default_selection_criteria(self, sample_dispatch: Dispatch) -> None:
        """Default selection criteria should be nearest_available."""
        assert sample_dispatch.selection_criteria == "nearest_available"

    def test_notes_initially_empty(self, sample_dispatch: Dispatch) -> None:
        """notes should be an empty list initially."""
        assert sample_dispatch.notes == []

    def test_vehicle_ids_property(self, sample_dispatch: Dispatch) -> None:
        """vehicle_ids property should return list of all vehicle IDs."""
        assert sample_dispatch.vehicle_ids == ["AMB-001"]

    def test_vehicle_ids_property_multiple_units(self) -> None:
        """vehicle_ids should return IDs for all units."""
        dispatch = Dispatch(
            emergency_id="some-emergency-id",
            units=[
                DispatchedUnit(vehicle_id="AMB-001", vehicle_type=VehicleType.AMBULANCE),
                DispatchedUnit(vehicle_id="FIRE-002", vehicle_type=VehicleType.FIRE_TRUCK),
            ],
        )
        assert set(dispatch.vehicle_ids) == {"AMB-001", "FIRE-002"}

    def test_all_acknowledged_true_when_all_ack(self) -> None:
        """all_acknowledged should be True when all units acknowledged."""
        ts = datetime(2026, 2, 10, 14, 32, 10, tzinfo=timezone.utc)
        dispatch = Dispatch(
            emergency_id="some-id",
            units=[
                DispatchedUnit(
                    vehicle_id="AMB-001",
                    vehicle_type=VehicleType.AMBULANCE,
                    acknowledged=True,
                    acknowledged_at=ts,
                ),
                DispatchedUnit(
                    vehicle_id="AMB-002",
                    vehicle_type=VehicleType.AMBULANCE,
                    acknowledged=True,
                    acknowledged_at=ts,
                ),
            ],
        )
        assert dispatch.all_acknowledged is True

    def test_all_acknowledged_false_when_partial(self, sample_dispatch: Dispatch) -> None:
        """all_acknowledged should be False if any unit has not acknowledged."""
        assert sample_dispatch.all_acknowledged is False

    def test_all_acknowledged_true_for_empty_units(self) -> None:
        """all_acknowledged should be True for a dispatch with no units (vacuous truth)."""
        dispatch = Dispatch(emergency_id="some-id", units=[])
        assert dispatch.all_acknowledged is True

    def test_two_dispatches_have_different_ids(self) -> None:
        """Each Dispatch should get a unique ID."""
        d1 = Dispatch(emergency_id="id-1", units=[])
        d2 = Dispatch(emergency_id="id-2", units=[])
        assert d1.dispatch_id != d2.dispatch_id

    def test_dispatch_serialization(self, sample_dispatch: Dispatch) -> None:
        """Dispatch should serialize to dict without errors."""
        data = sample_dispatch.model_dump()
        assert "dispatch_id" in data
        assert data["emergency_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert len(data["units"]) == 1

    def test_dispatch_json_roundtrip(self, sample_dispatch: Dispatch) -> None:
        """Dispatch should survive a JSON round-trip."""
        json_str = sample_dispatch.model_dump_json()
        restored = Dispatch.model_validate_json(json_str)
        assert restored.dispatch_id == sample_dispatch.dispatch_id
        assert restored.emergency_id == sample_dispatch.emergency_id


# ---------------------------------------------------------------------------
# VehicleStatusSnapshot model
# ---------------------------------------------------------------------------


@pytest.mark.unit
@pytest.mark.models
class TestVehicleStatusSnapshot:
    """Tests for VehicleStatusSnapshot model."""

    def test_valid_creation(self, sample_vehicle_snapshot: VehicleStatusSnapshot) -> None:
        """VehicleStatusSnapshot should be created with valid data."""
        assert sample_vehicle_snapshot.vehicle_id == "AMB-001"
        assert sample_vehicle_snapshot.vehicle_type == VehicleType.AMBULANCE
        assert sample_vehicle_snapshot.operational_status == OperationalStatus.IDLE

    def test_default_status_is_offline(self) -> None:
        """Default operational status should be OFFLINE for a new snapshot."""
        snap = VehicleStatusSnapshot(
            vehicle_id="AMB-002",
            vehicle_type=VehicleType.AMBULANCE,
        )
        assert snap.operational_status == OperationalStatus.OFFLINE

    def test_is_available_true_when_idle_no_alert(
        self, sample_vehicle_snapshot: VehicleStatusSnapshot
    ) -> None:
        """is_available should be True when IDLE and no active alert."""
        assert sample_vehicle_snapshot.is_available is True

    def test_is_available_false_when_en_route(self, sample_location: GeoLocation) -> None:
        """is_available should be False when en_route."""
        snap = VehicleStatusSnapshot(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
            operational_status=OperationalStatus.EN_ROUTE,
            location=sample_location,
        )
        assert snap.is_available is False

    def test_is_available_false_when_has_alert(self, sample_location: GeoLocation) -> None:
        """is_available should be False when idle but has an active alert."""
        snap = VehicleStatusSnapshot(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
            operational_status=OperationalStatus.IDLE,
            location=sample_location,
            has_active_alert=True,
        )
        assert snap.is_available is False

    def test_is_available_false_when_offline(self) -> None:
        """is_available should be False when OFFLINE."""
        snap = VehicleStatusSnapshot(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
            operational_status=OperationalStatus.OFFLINE,
        )
        assert snap.is_available is False

    def test_last_seen_at_auto_set(self, sample_vehicle_snapshot: VehicleStatusSnapshot) -> None:
        """last_seen_at should be set automatically."""
        assert sample_vehicle_snapshot.last_seen_at is not None
        assert isinstance(sample_vehicle_snapshot.last_seen_at, datetime)

    def test_current_emergency_id_initially_none(
        self, sample_vehicle_snapshot: VehicleStatusSnapshot
    ) -> None:
        """current_emergency_id should be None by default."""
        assert sample_vehicle_snapshot.current_emergency_id is None

    def test_location_is_optional(self) -> None:
        """VehicleStatusSnapshot should accept None location."""
        snap = VehicleStatusSnapshot(
            vehicle_id="AMB-999",
            vehicle_type=VehicleType.AMBULANCE,
        )
        assert snap.location is None

    def test_fuel_level_bounds(self, sample_location: GeoLocation) -> None:
        """fuel_level_percent should reject values outside 0-100."""
        with pytest.raises(ValueError):
            VehicleStatusSnapshot(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                location=sample_location,
                fuel_level_percent=101.0,
            )
        with pytest.raises(ValueError):
            VehicleStatusSnapshot(
                vehicle_id="AMB-001",
                vehicle_type=VehicleType.AMBULANCE,
                location=sample_location,
                fuel_level_percent=-1.0,
            )

    def test_snapshot_with_emergency_assigned(self, sample_location: GeoLocation) -> None:
        """Snapshot should correctly store current emergency ID."""
        snap = VehicleStatusSnapshot(
            vehicle_id="AMB-001",
            vehicle_type=VehicleType.AMBULANCE,
            operational_status=OperationalStatus.EN_ROUTE,
            location=sample_location,
            current_emergency_id="emergency-abc-123",
        )
        assert snap.current_emergency_id == "emergency-abc-123"
        assert snap.is_available is False

    def test_snapshot_serialization(self, sample_vehicle_snapshot: VehicleStatusSnapshot) -> None:
        """Snapshot should serialize to dict without errors."""
        data = sample_vehicle_snapshot.model_dump()
        assert data["vehicle_id"] == "AMB-001"
        assert data["vehicle_type"] == "ambulance"
        assert data["operational_status"] == "idle"

    def test_snapshot_json_roundtrip(self, sample_vehicle_snapshot: VehicleStatusSnapshot) -> None:
        """Snapshot should survive a JSON round-trip."""
        json_str = sample_vehicle_snapshot.model_dump_json()
        restored = VehicleStatusSnapshot.model_validate_json(json_str)
        assert restored.vehicle_id == sample_vehicle_snapshot.vehicle_id
        assert restored.operational_status == sample_vehicle_snapshot.operational_status
        assert restored.is_available == sample_vehicle_snapshot.is_available
