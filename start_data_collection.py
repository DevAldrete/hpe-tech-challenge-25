import asyncio
import os

from src.models.enums import VehicleType
from src.orchestrator.agent import OrchestratorAgent
from src.storage.database import db
from src.vehicle_agent.agent import VehicleAgent
from src.vehicle_agent.config import AgentConfig
from src.vehicle_agent.failure_injector import FailureScenario

# Ensure DATABASE_URL is set
if not os.getenv("DATABASE_URL"):
    os.environ["DATABASE_URL"] = (
        "postgresql+asyncpg://aegis_user:aegis_secure_pass_2026@localhost:5432/aegis_db"
    )


async def run_data_collection():
    print("Starting database connection...")
    db.connect()

    print("Starting OrchestratorAgent...")
    orchestrator = OrchestratorAgent(redis_host="localhost")
    orch_task = asyncio.create_task(orchestrator.run())

    print("Starting Fleet (2 Ambulances, 1 Fire Truck)...")
    configs = [
        AgentConfig(
            vehicle_id="AMB-001", vehicle_type=VehicleType.AMBULANCE, telemetry_frequency_hz=1.0
        ),
        AgentConfig(
            vehicle_id="AMB-002", vehicle_type=VehicleType.AMBULANCE, telemetry_frequency_hz=1.0
        ),
        AgentConfig(
            vehicle_id="FIRE-001", vehicle_type=VehicleType.FIRE_TRUCK, telemetry_frequency_hz=1.0
        ),
    ]

    agents = [VehicleAgent(cfg) for cfg in configs]

    # Activate a failure scenario for AMB-001 so we can capture anomaly data
    agents[0].failure_injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

    # Activate a different scenario for FIRE-001
    agents[2].failure_injector.activate_scenario(FailureScenario.BATTERY_DEGRADATION)

    fleet_tasks = [asyncio.create_task(agent.run()) for agent in agents]

    print("Data collection running. Will stop in 60 seconds...")
    try:
        await asyncio.wait_for(asyncio.gather(orch_task, *fleet_tasks), timeout=60.0)
    except TimeoutError:
        print("\nTime's up! Stopping data collection.")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await orchestrator.stop()
        for agent in agents:
            await agent.stop()
        await db.disconnect()


if __name__ == "__main__":
    try:
        asyncio.run(run_data_collection())
    except KeyboardInterrupt:
        print("\nData collection stopped by user.")
