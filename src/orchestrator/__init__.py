"""
Orchestrator package for Project AEGIS.

Central coordinator that manages fleet state, processes emergencies,
and dispatches units via Redis pub/sub and FastAPI REST + WebSocket.
"""

from src.orchestrator.agent import OrchestratorAgent
from src.orchestrator.api import create_app
from src.orchestrator.dispatch_engine import DispatchEngine

__all__ = [
    "OrchestratorAgent",
    "DispatchEngine",
    "create_app",
]
