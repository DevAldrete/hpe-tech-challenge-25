"""Vehicle agent package for Project AEGIS."""

from src.vehicle_agent.agent import VehicleAgent
from src.vehicle_agent.anomaly_detector import AnomalyDetector
from src.vehicle_agent.config import AgentConfig
from src.vehicle_agent.failure_injector import FailureInjector
from src.vehicle_agent.redis_client import RedisClient
from src.vehicle_agent.telemetry_generator import SimpleTelemetryGenerator

__all__ = [
    "VehicleAgent",
    "AgentConfig",
    "RedisClient",
    "SimpleTelemetryGenerator",
    "FailureInjector",
    "AnomalyDetector",
]
