"""
Repository classes for database operations.
"""

from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.alerts import PredictiveAlert
from src.models.telemetry import VehicleTelemetry
from src.storage.models import AlertRecord, TelemetryRecord, VehicleRecord


class TelemetryRepository:
    """Repository for telemetry data operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_telemetry(self, telemetry: VehicleTelemetry, vehicle_id: str) -> None:
        """
        Save a telemetry record to the database.

        Args:
            telemetry: The telemetry model to save.
            vehicle_id: The ID of the vehicle emitting this telemetry.
        """
        record = TelemetryRecord(
            vehicle_id=vehicle_id,
            timestamp=telemetry.timestamp,
            latitude=telemetry.latitude,
            longitude=telemetry.longitude,
            speed=telemetry.speed_kmh,
            engine_temp=telemetry.engine_temp_celsius,
            battery_voltage=telemetry.battery_voltage,
            fuel_level=telemetry.fuel_level_percent,
            odometer=telemetry.odometer_km,
        )
        self.session.add(record)

    async def upsert_vehicle(self, vehicle_id: str, vehicle_type: str, status: str) -> None:
        """
        Insert or update vehicle metadata.
        """
        stmt = insert(VehicleRecord).values(
            vehicle_id=vehicle_id,
            vehicle_type=vehicle_type,
            status=status,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["vehicle_id"],
            set_={
                "vehicle_type": stmt.excluded.vehicle_type,
                "status": stmt.excluded.status,
            },
        )
        await self.session.execute(stmt)


class AlertRepository:
    """Repository for predictive alerts operations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def save_alert(self, alert: PredictiveAlert, vehicle_id: str) -> None:
        """
        Save an alert record to the database.

        Args:
            alert: The predictive alert to save.
            vehicle_id: The ID of the vehicle experiencing the alert.
        """
        record = AlertRecord(
            vehicle_id=vehicle_id,
            alert_type=alert.category.value,
            severity=alert.severity.value,
            title=f"Alert: {alert.category.value} - {alert.component}",
            description=alert.recommended_action,
            probability=alert.failure_probability,
            confidence=alert.confidence,
            detected_at=alert.timestamp,
            telemetry_snapshot=alert.related_telemetry,
            status="active",
        )
        self.session.add(record)
