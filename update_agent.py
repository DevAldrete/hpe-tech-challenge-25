import re

with open("src/orchestrator/agent.py", "r") as f:
    content = f.read()

# Remove imports
content = re.sub(
    r"from src.models.enums import MessageType, OperationalStatus, VehicleType\nfrom src.models.messages import Message",
    "from src.models.enums import OperationalStatus, VehicleType\nfrom src.models.telemetry import VehicleTelemetry\nfrom src.models.alerts import PredictiveAlert",
    content,
)

# Remove heartbeat pattern
content = re.sub(r'HEARTBEAT_PATTERN = "aegis:\*:heartbeat:\*"\n', "", content)
content = re.sub(r"            HEARTBEAT_PATTERN,\n", "", content)

# Update _handle_raw_message
handle_raw_old = """    async def _handle_raw_message(self, raw: dict) -> None:
        \"\"\"Parse and dispatch an incoming Redis pub/sub message.

        Args:
            raw: Raw message dict from redis-py pubsub listener.
        \"\"\"
        channel: str = raw.get("channel", "") or raw.get("pattern", "") or ""
        data: str = raw.get("data", "")

        if not data or not isinstance(data, str):
            return

        try:
            message = Message.model_validate_json(data)
        except Exception as e:
            logger.warning("message_parse_error", channel=channel, error=str(e))
            return

        if message.message_type == MessageType.TELEMETRY_UPDATE:
            await self._handle_telemetry(message)
        elif message.message_type == MessageType.HEARTBEAT:
            await self._handle_heartbeat(message)
        elif message.message_type == MessageType.ALERT_GENERATED:
            await self._handle_alert(message)
        else:
            logger.debug(
                "unhandled_message_type",
                message_type=message.message_type.value,
                source=message.source,
            )"""

handle_raw_new = """    async def _handle_raw_message(self, raw: dict) -> None:
        \"\"\"Parse and dispatch an incoming Redis pub/sub message.

        Args:
            raw: Raw message dict from redis-py pubsub listener.
        \"\"\"
        channel: str = raw.get("channel", "") or raw.get("pattern", "") or ""
        data: str = raw.get("data", "")

        if not data or not isinstance(data, str):
            return

        try:
            if "telemetry" in channel:
                telemetry = VehicleTelemetry.model_validate_json(data)
                await self._handle_telemetry(telemetry)
            elif "alerts" in channel:
                alert = PredictiveAlert.model_validate_json(data)
                await self._handle_alert(alert)
            else:
                logger.debug("unhandled_channel", channel=channel)
        except Exception as e:
            logger.warning("message_parse_error", channel=channel, error=str(e))
            return"""

content = content.replace(handle_raw_old, handle_raw_new)

# Update _handle_telemetry
handle_tel_old = """    async def _handle_telemetry(self, message: Message) -> None:
        \"\"\"Update fleet state from a telemetry message.

        Args:
            message: Telemetry Message envelope from a vehicle.
        \"\"\"
        vehicle_id = message.source
        telemetry_data = message.payload.get("telemetry", {})

        snap = self.fleet.get(vehicle_id)
        if snap is None:
            # First time seeing this vehicle - infer type from ID prefix
            vehicle_type = _infer_vehicle_type(vehicle_id)
            snap = VehicleStatusSnapshot(
                vehicle_id=vehicle_id,
                vehicle_type=vehicle_type,
                operational_status=OperationalStatus.IDLE,
            )
            self.fleet[vehicle_id] = snap
            logger.info("new_vehicle_registered", vehicle_id=vehicle_id, type=vehicle_type.value)

        # Update last seen timestamp
        snap.last_seen_at = datetime.utcnow()

        # Update location if present
        if "location" in telemetry_data:
            from src.models.vehicle import Location

            try:
                snap.location = Location.model_validate(telemetry_data["location"])
            except Exception:
                pass  # Location parse failure is non-fatal

        # Update key health metrics
        if "battery_voltage" in telemetry_data:
            snap.battery_voltage = float(telemetry_data["battery_voltage"])
        if "fuel_level_percent" in telemetry_data:
            snap.fuel_level_percent = float(telemetry_data["fuel_level_percent"])

        logger.debug("telemetry_processed", vehicle_id=vehicle_id)"""

handle_tel_new = """    async def _handle_telemetry(self, telemetry: VehicleTelemetry) -> None:
        \"\"\"Update fleet state from a telemetry message.

        Args:
            telemetry: VehicleTelemetry payload from a vehicle.
        \"\"\"
        vehicle_id = telemetry.vehicle_id

        snap = self.fleet.get(vehicle_id)
        if snap is None:
            # First time seeing this vehicle - infer type from ID prefix
            vehicle_type = _infer_vehicle_type(vehicle_id)
            snap = VehicleStatusSnapshot(
                vehicle_id=vehicle_id,
                vehicle_type=vehicle_type,
                operational_status=OperationalStatus.IDLE,
            )
            self.fleet[vehicle_id] = snap
            logger.info("new_vehicle_registered", vehicle_id=vehicle_id, type=vehicle_type.value)

        # Update last seen timestamp
        snap.last_seen_at = datetime.utcnow()

        # Update location
        from src.models.vehicle import Location
        try:
            snap.location = Location(
                latitude=telemetry.latitude,
                longitude=telemetry.longitude,
                timestamp=telemetry.timestamp
            )
        except Exception:
            pass  # Location parse failure is non-fatal

        # Update key health metrics
        snap.battery_voltage = float(telemetry.battery_voltage)
        snap.fuel_level_percent = float(telemetry.fuel_level_percent)

        logger.debug("telemetry_processed", vehicle_id=vehicle_id)"""

content = content.replace(handle_tel_old, handle_tel_new)

# Update _handle_alert and remove _handle_heartbeat
handle_hb_al_old = """    async def _handle_heartbeat(self, message: Message) -> None:
        \"\"\"Update fleet state from a heartbeat message.

        Args:
            message: Heartbeat Message envelope from a vehicle.
        \"\"\"
        vehicle_id = message.source
        if vehicle_id in self.fleet:
            self.fleet[vehicle_id].last_seen_at = datetime.utcnow()
            logger.debug("heartbeat_received", vehicle_id=vehicle_id)

    async def _handle_alert(self, message: Message) -> None:
        \"\"\"Mark a vehicle as having an active alert.

        Args:
            message: Alert Message envelope from a vehicle.
        \"\"\"
        vehicle_id = message.source
        if vehicle_id in self.fleet:
            self.fleet[vehicle_id].has_active_alert = True
        logger.info("alert_received", vehicle_id=vehicle_id, payload=message.payload)"""

handle_al_new = """    async def _handle_alert(self, alert: PredictiveAlert) -> None:
        \"\"\"Mark a vehicle as having an active alert.

        Args:
            alert: PredictiveAlert payload from a vehicle.
        \"\"\"
        vehicle_id = alert.vehicle_id
        if vehicle_id in self.fleet:
            self.fleet[vehicle_id].has_active_alert = True
        logger.info("alert_received", vehicle_id=vehicle_id, alert_id=alert.alert_id)"""

content = content.replace(handle_hb_al_old, handle_al_new)

with open("src/orchestrator/agent.py", "w") as f:
    f.write(content)
