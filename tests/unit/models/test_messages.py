"""
Unit tests for messages.py models.

Tests cover Message envelope and all payload types.
"""

import pytest
from pydantic import ValidationError

from src.models.enums import CommandType, MessagePriority, MessageType
from src.models.messages import (
    AlertAcknowledgmentPayload,
    CommandPayload,
    FleetStatusPayload,
    HeartbeatPayload,
    LocalDecisionPayload,
    Message,
)


@pytest.mark.unit
@pytest.mark.models
class TestMessage:
    """Test Message envelope model validation and behavior."""

    def test_message_valid_creation(self, sample_message_data: dict) -> None:
        """Test creating a valid Message instance."""
        message = Message(**sample_message_data)
        assert message.message_type == MessageType.TELEMETRY_UPDATE
        assert message.source == "AMB-001"
        assert message.destination == "orchestrator"
        assert message.priority == MessagePriority.NORMAL
        assert message.payload == {"test": "data"}
        assert message.ttl_seconds == 60

    def test_message_auto_generates_id(self, sample_message_data: dict) -> None:
        """Test message_id is auto-generated if not provided."""
        message = Message(**sample_message_data)
        assert message.message_id is not None
        assert isinstance(message.message_id, str)
        assert len(message.message_id) > 0

    def test_message_type_enum(self, sample_message_data: dict) -> None:
        """Test message_type must be valid MessageType enum."""
        for msg_type in MessageType:
            sample_message_data["message_type"] = msg_type
            message = Message(**sample_message_data)
            assert message.message_type == msg_type

    def test_message_priority_enum(self, sample_message_data: dict) -> None:
        """Test priority must be valid MessagePriority enum."""
        for priority in MessagePriority:
            sample_message_data["priority"] = priority
            message = Message(**sample_message_data)
            assert message.priority == priority

    def test_message_priority_defaults_to_normal(self, sample_message_data: dict) -> None:
        """Test priority defaults to NORMAL if not provided."""
        del sample_message_data["priority"]
        message = Message(**sample_message_data)
        assert message.priority == MessagePriority.NORMAL

    def test_message_destination_optional(self, sample_message_data: dict) -> None:
        """Test destination can be None for broadcast messages."""
        sample_message_data["destination"] = None
        message = Message(**sample_message_data)
        assert message.destination is None

    def test_message_correlation_id_optional(self, sample_message_data: dict) -> None:
        """Test correlation_id is optional."""
        message = Message(**sample_message_data)
        assert message.correlation_id is None

        sample_message_data["correlation_id"] = "corr-123"
        message = Message(**sample_message_data)
        assert message.correlation_id == "corr-123"

    def test_message_schema_version_default(self, sample_message_data: dict) -> None:
        """Test schema_version defaults to 1.0.0."""
        message = Message(**sample_message_data)
        assert message.schema_version == "1.0.0"

    def test_message_compressed_defaults_to_false(self, sample_message_data: dict) -> None:
        """Test compressed defaults to False."""
        message = Message(**sample_message_data)
        assert message.compressed is False

    def test_message_serialization(self, sample_message_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        message = Message(**sample_message_data)
        json_data = message.model_dump()

        assert json_data["message_type"] == "telemetry.update"
        assert json_data["source"] == "AMB-001"

        # Test round-trip
        message_from_json = Message(**json_data)
        assert message_from_json.source == message.source
        assert message_from_json.payload == message.payload


@pytest.mark.unit
@pytest.mark.models
class TestHeartbeatPayload:
    """Test HeartbeatPayload model validation and behavior."""

    def test_heartbeat_payload_valid_creation(self, sample_heartbeat_payload_data: dict) -> None:
        """Test creating a valid HeartbeatPayload instance."""
        payload = HeartbeatPayload(**sample_heartbeat_payload_data)
        assert payload.vehicle_id == "AMB-001"
        assert payload.uptime_seconds == 86400
        assert payload.last_telemetry_sequence == 12345
        assert payload.agent_version == "1.0.0"
        assert payload.system_health["cpu_percent"] == 15.5
        assert payload.system_health["redis_connected"] is True

    def test_heartbeat_payload_uptime_non_negative(
        self, sample_heartbeat_payload_data: dict
    ) -> None:
        """Test uptime_seconds must be non-negative."""
        sample_heartbeat_payload_data["uptime_seconds"] = -1
        with pytest.raises(ValidationError):
            HeartbeatPayload(**sample_heartbeat_payload_data)

    def test_heartbeat_payload_system_health_default(self) -> None:
        """Test system_health has sensible defaults."""
        payload = HeartbeatPayload(
            vehicle_id="AMB-001",
            uptime_seconds=100,
            last_telemetry_sequence=1,
            agent_version="1.0.0",
        )
        assert "cpu_percent" in payload.system_health
        assert "redis_connected" in payload.system_health


@pytest.mark.unit
@pytest.mark.models
class TestCommandPayload:
    """Test CommandPayload model validation and behavior."""

    def test_command_payload_valid_creation(self, sample_command_payload_data: dict) -> None:
        """Test creating a valid CommandPayload instance."""
        payload = CommandPayload(**sample_command_payload_data)
        assert payload.command_type == CommandType.DISPATCH
        assert payload.reason == "Cardiac arrest reported"
        assert payload.issued_by == "dispatcher_user_42"
        assert payload.requires_acknowledgment is True
        assert "mission_id" in payload.parameters

    def test_command_payload_type_enum(self, sample_command_payload_data: dict) -> None:
        """Test command_type must be valid CommandType enum."""
        for cmd_type in CommandType:
            sample_command_payload_data["command_type"] = cmd_type
            payload = CommandPayload(**sample_command_payload_data)
            assert payload.command_type == cmd_type

    def test_command_payload_parameters_default(self, sample_command_payload_data: dict) -> None:
        """Test parameters defaults to empty dict."""
        del sample_command_payload_data["parameters"]
        payload = CommandPayload(**sample_command_payload_data)
        assert payload.parameters == {}

    def test_command_payload_requires_ack_default(self, sample_command_payload_data: dict) -> None:
        """Test requires_acknowledgment defaults to True."""
        del sample_command_payload_data["requires_acknowledgment"]
        payload = CommandPayload(**sample_command_payload_data)
        assert payload.requires_acknowledgment is True


@pytest.mark.unit
@pytest.mark.models
class TestLocalDecisionPayload:
    """Test LocalDecisionPayload model validation and behavior."""

    def test_local_decision_payload_valid_creation(self) -> None:
        """Test creating a valid LocalDecisionPayload instance."""
        payload = LocalDecisionPayload(
            vehicle_id="AMB-001",
            decision_type="limp_mode_activated",
            reason="Engine temperature exceeded 120°C",
            telemetry_snapshot={"engine_temp_celsius": 125.5},
            action_taken="Reduced max RPM to 2000",
        )
        assert payload.vehicle_id == "AMB-001"
        assert payload.decision_type == "limp_mode_activated"
        assert payload.requires_orchestrator_override is False

    def test_local_decision_payload_alert_ids_default(self) -> None:
        """Test alert_ids defaults to empty list."""
        payload = LocalDecisionPayload(
            vehicle_id="AMB-001",
            decision_type="emergency_brake",
            reason="Obstacle detected",
            telemetry_snapshot={},
            action_taken="Applied emergency brake",
        )
        assert payload.alert_ids == []


@pytest.mark.unit
@pytest.mark.models
class TestAlertAcknowledgmentPayload:
    """Test AlertAcknowledgmentPayload model validation and behavior."""

    def test_alert_acknowledgment_payload_valid_creation(self) -> None:
        """Test creating a valid AlertAcknowledgmentPayload instance."""
        payload = AlertAcknowledgmentPayload(
            alert_id="alert-123",
            acknowledged_by="orchestrator",
            action_taken="Maintenance scheduled",
        )
        assert payload.alert_id == "alert-123"
        assert payload.acknowledged_by == "orchestrator"
        assert payload.action_taken == "Maintenance scheduled"
        assert payload.override_recommendation is False

    def test_alert_acknowledgment_override_default(self) -> None:
        """Test override_recommendation defaults to False."""
        payload = AlertAcknowledgmentPayload(
            alert_id="alert-123",
            acknowledged_by="dispatcher",
            action_taken="Ignored",
        )
        assert payload.override_recommendation is False


@pytest.mark.unit
@pytest.mark.models
class TestFleetStatusPayload:
    """Test FleetStatusPayload model validation and behavior."""

    def test_fleet_status_payload_valid_creation(self, sample_datetime) -> None:
        """Test creating a valid FleetStatusPayload instance."""
        payload = FleetStatusPayload(
            fleet_id="fleet01",
            timestamp=sample_datetime,
            total_vehicles=10,
            status_summary={"idle": 5, "en_route": 3},
            active_alerts={"critical": 0, "warning": 2},
            active_missions=4,
        )
        assert payload.fleet_id == "fleet01"
        assert payload.total_vehicles == 10
        assert payload.active_missions == 4

    def test_fleet_status_payload_total_vehicles_non_negative(self, sample_datetime) -> None:
        """Test total_vehicles must be non-negative."""
        with pytest.raises(ValidationError):
            FleetStatusPayload(
                fleet_id="fleet01",
                timestamp=sample_datetime,
                total_vehicles=-1,
                status_summary={},
                active_alerts={},
                active_missions=0,
            )

    def test_fleet_status_payload_active_missions_non_negative(self, sample_datetime) -> None:
        """Test active_missions must be non-negative."""
        with pytest.raises(ValidationError):
            FleetStatusPayload(
                fleet_id="fleet01",
                timestamp=sample_datetime,
                total_vehicles=10,
                status_summary={},
                active_alerts={},
                active_missions=-1,
            )

    def test_fleet_status_payload_response_time_optional(self, sample_datetime) -> None:
        """Test average_response_time_seconds is optional."""
        payload = FleetStatusPayload(
            fleet_id="fleet01",
            timestamp=sample_datetime,
            total_vehicles=10,
            status_summary={},
            active_alerts={},
            active_missions=0,
        )
        assert payload.average_response_time_seconds is None

    def test_fleet_status_payload_response_time_non_negative(self, sample_datetime) -> None:
        """Test average_response_time_seconds must be non-negative when provided."""
        with pytest.raises(ValidationError):
            FleetStatusPayload(
                fleet_id="fleet01",
                timestamp=sample_datetime,
                total_vehicles=10,
                status_summary={},
                active_alerts={},
                active_missions=0,
                average_response_time_seconds=-1.0,
            )
