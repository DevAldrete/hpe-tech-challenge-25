"""
Storage module for data persistency.
"""

from src.storage.config import storage_config
from src.storage.database import Database, db
from src.storage.models import AlertRecord, Base, TelemetryRecord, VehicleRecord
from src.storage.repositories import AlertRepository, TelemetryRepository

__all__ = [
    "db",
    "Database",
    "Base",
    "VehicleRecord",
    "TelemetryRecord",
    "AlertRecord",
    "TelemetryRepository",
    "AlertRepository",
    "storage_config",
]
