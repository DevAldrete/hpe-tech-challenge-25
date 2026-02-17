"""
Communication protocol and message models for Project AEGIS.

This module contains message envelope and payload structures for Redis/WebSocket communication.
"""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.models.enums import CommandType, MessagePriority, MessageType


class Message(BaseModel):
    """Universal message envelope for all communications."""

    message_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique message identifier",
    )
    message_type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")

    source: str = Field(
        ..., description="Source identifier (vehicle_id, 'orchestrator', 'dashboard')"
    )
    destination: str | None = Field(None, description="Target identifier (None for broadcast)")

    priority: MessagePriority = Field(
        default=MessagePriority.NORMAL, description="Delivery priority"
    )
    correlation_id: str | None = Field(
        None, description="Correlation ID for request/response pairing"
    )

    payload: dict[str, Any] = Field(..., description="Message payload (type-specific)")
    ttl_seconds: int = Field(default=60, description="Time-to-live in seconds")

    # Metadata
    schema_version: str = Field(default="1.0.0", description="Message schema version")
    compressed: bool = Field(default=False, description="Whether payload is compressed")

    model_config = {
        "json_schema_extra": {
            "example": {
                "message_id": "550e8400-e29b-41d4-a716-446655440000",
                "message_type": "telemetry.update",
                "timestamp": "2026-02-10T14:32:01.000Z",
                "source": "AMB-001",
                "destination": "orchestrator",
                "priority": "normal",
                "payload": {"telemetry": "..."},
                "ttl_seconds": 60,
            }
        }
    }


# ============================================================================
# MESSAGE PAYLOADS
# ============================================================================


class HeartbeatPayload(BaseModel):
    """Health check payload sent every 10 seconds from vehicle to orchestrator."""

    vehicle_id: str
    uptime_seconds: int = Field(..., ge=0, description="Vehicle agent uptime")
    last_telemetry_sequence: int = Field(..., description="Last telemetry sequence number sent")
    agent_version: str = Field(..., description="Vehicle agent software version")
    system_health: dict[str, Any] = Field(
        default_factory=lambda: {
            "cpu_percent": 0.0,
            "memory_percent": 0.0,
            "disk_percent": 0.0,
            "network_latency_ms": 0.0,
            "redis_connected": True,
        },
        description="System health metrics",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "uptime_seconds": 86400,
                "last_telemetry_sequence": 12345,
                "agent_version": "1.0.0",
                "system_health": {
                    "cpu_percent": 15.5,
                    "memory_percent": 42.3,
                    "disk_percent": 58.1,
                    "network_latency_ms": 12.5,
                    "redis_connected": True,
                },
            }
        }
    }


class CommandPayload(BaseModel):
    """Commands sent from orchestrator to vehicle."""

    command_type: CommandType
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Command-specific parameters"
    )
    reason: str = Field(..., description="Reason for issuing command")
    issued_by: str = Field(..., description="User ID or 'system' that issued command")
    requires_acknowledgment: bool = Field(
        default=True, description="Whether vehicle must acknowledge"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "command_type": "dispatch",
                "parameters": {
                    "mission_id": "MISSION-2026-02-10-001",
                    "destination": {
                        "latitude": 37.8049,
                        "longitude": -122.4194,
                        "address": "123 Emergency St, San Francisco, CA",
                    },
                    "priority": "life_threatening",
                },
                "reason": "Cardiac arrest reported",
                "issued_by": "dispatcher_user_42",
                "requires_acknowledgment": True,
            }
        }
    }


class LocalDecisionPayload(BaseModel):
    """Vehicle reports autonomous decision made locally."""

    vehicle_id: str
    decision_type: str = Field(
        ...,
        description="Type of decision (limp_mode, emergency_brake, route_change, etc.)",
    )
    reason: str = Field(..., description="Reason for decision")
    telemetry_snapshot: dict[str, Any] = Field(
        ..., description="Relevant telemetry at decision time"
    )
    alert_ids: list[str] = Field(default_factory=list, description="Related alert IDs")
    action_taken: str = Field(..., description="Description of action taken")
    requires_orchestrator_override: bool = Field(
        default=False, description="Whether orchestrator can override"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "vehicle_id": "AMB-001",
                "decision_type": "limp_mode_activated",
                "reason": "Engine temperature exceeded 120°C",
                "telemetry_snapshot": {
                    "engine_temp_celsius": 125.5,
                    "coolant_temp_celsius": 118.0,
                    "engine_rpm": 3500,
                },
                "alert_ids": ["alert-550e8400"],
                "action_taken": "Reduced max RPM to 2000, activated hazard lights",
                "requires_orchestrator_override": False,
            }
        }
    }


class AlertAcknowledgmentPayload(BaseModel):
    """Orchestrator acknowledges receipt of alert."""

    alert_id: str
    acknowledged_by: str = Field(..., description="User/system that acknowledged")
    action_taken: str = Field(..., description="Action taken in response to alert")
    override_recommendation: bool = Field(
        default=False, description="Whether recommendation was overridden"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "alert_id": "alert-550e8400",
                "acknowledged_by": "orchestrator",
                "action_taken": "Maintenance scheduled for 2026-02-11 08:00",
                "override_recommendation": False,
            }
        }
    }


class FleetStatusPayload(BaseModel):
    """Aggregated fleet status for dashboard."""

    fleet_id: str
    timestamp: datetime
    total_vehicles: int = Field(..., ge=0, description="Total number of vehicles")
    status_summary: dict[str, int] = Field(
        ..., description="Count of vehicles per operational status"
    )
    active_alerts: dict[str, int] = Field(..., description="Count of alerts per severity level")
    active_missions: int = Field(..., ge=0, description="Number of active missions")
    average_response_time_seconds: float | None = Field(
        None, ge=0, description="Average response time"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "fleet_id": "fleet01",
                "timestamp": "2026-02-10T14:32:00.000Z",
                "total_vehicles": 10,
                "status_summary": {
                    "idle": 5,
                    "en_route": 3,
                    "on_scene": 1,
                    "maintenance": 1,
                    "offline": 0,
                },
                "active_alerts": {"critical": 0, "warning": 2, "info": 5},
                "active_missions": 4,
                "average_response_time_seconds": 180.0,
            }
        }
    }
