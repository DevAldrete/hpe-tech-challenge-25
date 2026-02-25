import re

with open("tests/unit/orchestrator/test_orchestrator_agent.py", "r") as f:
    content = f.read()

# Update imports
content = re.sub(
    r"from src.models.enums import MessagePriority, MessageType, OperationalStatus, VehicleType\nfrom src.models.messages import Message",
    "from src.models.enums import OperationalStatus, VehicleType\nfrom src.models.telemetry import VehicleTelemetry\nfrom src.models.alerts import PredictiveAlert\nfrom src.models.enums import AlertSeverity, FailureCategory",
    content,
)

# Remove Message dependencies
# Replace _make_telemetry_message to return VehicleTelemetry
telemetry_mock_old = """def _make_telemetry_message(
    vehicle_id: str = "AMB-001",
    lat: float = 19.44,
    lon: float = -99.14,
    battery_voltage: float = 13.8,
    fuel_level: float = 75.0,
) -> Message:
    \"\"\"Build a TELEMETRY_UPDATE Message envelope.\"\"\"
    return Message(
        message_type=MessageType.TELEMETRY_UPDATE,
        source=vehicle_id,
        destination="orchestrator",
        priority=MessagePriority.NORMAL,
        payload={
            "telemetry": {
                "vehicle_id": vehicle_id,
                "location": {
                    "latitude": lat,
                    "longitude": lon,
                    "altitude": 2240.0,
                    "accuracy": 10.0,
                    "heading": 0.0,
                    "speed_kmh": 0.0,
                    "timestamp": "2026-02-10T14:00:00+00:00",
                },
                "battery_voltage": battery_voltage,
                "fuel_level_percent": fuel_level,
            }
        },
    )"""

telemetry_mock_new = """def _make_telemetry_message(
    vehicle_id: str = "AMB-001",
    lat: float = 19.44,
    lon: float = -99.14,
    battery_voltage: float = 13.8,
    fuel_level: float = 75.0,
) -> VehicleTelemetry:
    \"\"\"Build a VehicleTelemetry model.\"\"\"
    return VehicleTelemetry(
        vehicle_id=vehicle_id,
        timestamp=datetime.now(timezone.utc),
        latitude=lat,
        longitude=lon,
        speed_kmh=0.0,
        odometer_km=1000.0,
        engine_temp_celsius=90.0,
        battery_voltage=battery_voltage,
        fuel_level_percent=fuel_level,
    )"""

content = content.replace(telemetry_mock_old, telemetry_mock_new)

# Remove _make_heartbeat_message
heartbeat_mock_old = """def _make_heartbeat_message(vehicle_id: str = "AMB-001") -> Message:
    \"\"\"Build a HEARTBEAT Message envelope.\"\"\"
    return Message(
        message_type=MessageType.HEARTBEAT,
        source=vehicle_id,
        destination="orchestrator",
        priority=MessagePriority.LOW,
        payload={
            "vehicle_id": vehicle_id,
            "uptime_seconds": 300,
            "last_telemetry_sequence": 100,
            "agent_version": "1.0.0",
        },
    )"""

content = content.replace(heartbeat_mock_old, "")

# Update tests that use heartbeat
heartbeat_test_old_1 = """    @pytest.mark.asyncio
    async def test_heartbeat_updates_last_seen(self) -> None:
        \"\"\"Heartbeat should update last_seen_at for known vehicles.\"\"\"
        orch = _make_orchestrator()

        # Register vehicle first via telemetry
        await orch._handle_telemetry(_make_telemetry_message("AMB-001"))
        first_seen = orch.fleet["AMB-001"].last_seen_at

        # Small delay then send heartbeat
        await orch._handle_heartbeat(_make_heartbeat_message("AMB-001"))
        second_seen = orch.fleet["AMB-001"].last_seen_at

        assert second_seen >= first_seen"""

content = content.replace(heartbeat_test_old_1, "")

heartbeat_test_old_2 = """    @pytest.mark.asyncio
    async def test_heartbeat_ignores_unknown_vehicles(self) -> None:
        \"\"\"Heartbeat from an unknown vehicle should not crash or add to fleet.\"\"\"
        orch = _make_orchestrator()
        msg = _make_heartbeat_message("UNKNOWN-999")
        await orch._handle_heartbeat(msg)  # Should not raise
        assert "UNKNOWN-999" not in orch.fleet"""

content = content.replace(heartbeat_test_old_2, "")

# Update alert test
alert_test_old = """    @pytest.mark.asyncio
    async def test_alert_marks_vehicle_has_active_alert(self) -> None:
        \"\"\"Alert message should mark the vehicle as having an active alert.\"\"\"
        orch = _make_orchestrator()
        await orch._handle_telemetry(_make_telemetry_message("AMB-001"))
        assert orch.fleet["AMB-001"].has_active_alert is False

        alert_msg = Message(
            message_type=MessageType.ALERT_GENERATED,
            source="AMB-001",
            destination="orchestrator",
            priority=MessagePriority.HIGH,
            payload={"alert": {"severity": "warning", "component": "alternator"}},
        )
        await orch._handle_alert(alert_msg)
        assert orch.fleet["AMB-001"].has_active_alert is True"""

alert_test_new = """    @pytest.mark.asyncio
    async def test_alert_marks_vehicle_has_active_alert(self) -> None:
        \"\"\"Alert message should mark the vehicle as having an active alert.\"\"\"
        orch = _make_orchestrator()
        await orch._handle_telemetry(_make_telemetry_message("AMB-001"))
        assert orch.fleet["AMB-001"].has_active_alert is False

        alert_msg = PredictiveAlert(
            vehicle_id="AMB-001",
            timestamp=datetime.now(timezone.utc),
            severity=AlertSeverity.WARNING,
            category=FailureCategory.ELECTRICAL,
            component="alternator",
            failure_probability=0.8,
            confidence=0.9,
            predicted_failure_min_hours=1.0,
            predicted_failure_max_hours=5.0,
            predicted_failure_likely_hours=3.0,
            can_complete_current_mission=True,
            safe_to_operate=True,
            recommended_action="Inspect alternator"
        )
        await orch._handle_alert(alert_msg)
        assert orch.fleet["AMB-001"].has_active_alert is True"""

content = content.replace(alert_test_old, alert_test_new)

with open("tests/unit/orchestrator/test_orchestrator_agent.py", "w") as f:
    f.write(content)
