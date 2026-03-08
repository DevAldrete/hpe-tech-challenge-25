# Architecture Overview - Project AEGIS

**Version:** 2.1.0  
**Last Updated:** 2026-03-08

This is the code-aligned architecture for the current implementation in `src/`.

## What the System Is

AEGIS is an event-driven emergency fleet simulator with two runtime actors:

- `VehicleAgent` (`src/vehicle_agent/agent.py`) simulates a single vehicle and publishes telemetry/alerts.
- `OrchestratorAgent` (`src/orchestrator/agent.py`) maintains fleet and emergency state, decides dispatch, and coordinates incident lifecycle.

Both communicate through the `MessageBus` contract (`src/core/messaging.py`) so runtime and tests can swap transports.

## Essential Building Blocks

### 1) Vehicle runtime (`src/vehicle_agent/`)

- Runs a fixed-frequency tick loop (`VehicleAgent._tick`).
- Tick order matters:
  1. evaluate scheduled failures,
  2. handle maintenance timer,
  3. generate baseline telemetry,
  4. apply active failure scenarios,
  5. run anomaly detection,
  6. publish telemetry,
  7. publish alerts.
- Subscribes to:
  - per-vehicle command channel for `dispatch`,
  - global resolve pattern for `resolve`.

### 2) Orchestrator runtime (`src/orchestrator/`)

- Subscribes to fleet-wide telemetry, alerts, registration, and dispatch ack channels.
- Delegates business logic to:
  - `FleetService` (`src/orchestrator/fleet_service.py`) for vehicle snapshots and alert flags,
  - `EmergencyService` (`src/orchestrator/emergency_service.py`) for emergency status and timeout policy,
  - `DispatchEngine` (`src/orchestrator/dispatch_engine.py`) for nearest-available unit selection.
- Persists side effects asynchronously via persisters in `src/orchestrator/persistence.py`.

### 3) Transport abstraction (`src/core/messaging.py`)

- Runtime adapter: `RedisMessageBus` (`src/infrastructure/redis_bus.py`).
- Deterministic test adapter: `InMemoryMessageBus` (`src/infrastructure/in_memory_bus.py`).

### 4) Time abstraction (`src/core/time.py`)

- `RealClock` for normal execution.
- `FastForwardClock` for deterministic tests and accelerated simulation mode.

### 5) API + real-time stream (`src/orchestrator/api.py`)

- FastAPI endpoints expose fleet, emergencies, alerts, timeline, and analytics.
- WebSocket (`/ws`) broadcasts live events (`telemetry.update`, emergency events, prediction events).

### 6) Simulation and AI engine (`src/orchestrator/emergency_generator.py`, `src/orchestrator/historical_injector.py`, `src/ml/`)

- AI predictor uses a trained Random Forest model to forecast high-risk zones for proactive dispatch.
- Historical injector emits holdout crimes to validate prediction quality in live simulation.
- Both generators follow `Clock` for deterministic, time-travel-friendly simulation behavior.

## Core Runtime Flows

### Flow 0: Train model artifacts

Before running orchestrator flows that depend on prediction, train the model artifacts:

```bash
python src/ml/train_crime.py
```

### Flow A: Vehicle startup and registration

1. Vehicle agent starts and connects to message bus.
2. It immediately publishes `VehicleRegistrationEvent`.
3. Orchestrator records/updates the vehicle snapshot before steady-state telemetry.

### Flow B: Telemetry update loop

1. Vehicle publishes `VehicleTelemetry` every tick.
2. Orchestrator updates in-memory `VehicleStatusSnapshot`.
3. Orchestrator enqueues telemetry persistence (non-blocking).
4. If configured, orchestrator broadcasts live telemetry over WebSocket.

### Flow C: Alert and maintenance loop

1. Vehicle emits `PredictiveAlert` when anomaly detector/rules trigger.
2. Orchestrator marks `has_active_alert=True` and persists alert.
3. Critical failures can move vehicle to `MAINTENANCE`.
4. After repair window, vehicle publishes `alerts_cleared`.
5. Orchestrator clears alert state and retries waiting emergencies.

### Flow D: Dispatch and coordination lifecycle

1. Emergency is created (API or event channel).
2. `DispatchEngine` selects nearest available units by type.
3. Orchestrator publishes `dispatch` command to each selected vehicle.
4. Vehicles ack on `aegis:dispatch:{emergency_id}:ack`.
5. Vehicles transition `EN_ROUTE -> ON_SCENE` after arrival.
6. Orchestrator marks emergency `IN_PROGRESS`, advances coordination checkpoints.
7. When coordination tasks are complete, orchestrator resolves emergency and broadcasts `resolve`.

### Flow E: Stale emergency sweeper

Background sweeper (`OrchestratorAgent._emergency_sweeper`) enforces lifecycle deadlines:

- `DISPATCHING` too long -> `CANCELLED`
- `DISPATCHED` stalled too long -> `DISMISSED`
- `IN_PROGRESS` over planned duration -> auto `RESOLVED`
- `IN_PROGRESS` over hard max duration -> `DISMISSED`

## Design Rules That Drive This Architecture

- Keep dispatch/control loop in memory for low-latency decisions.
- Treat database writes as asynchronous side effects, not control-loop dependencies.
- Keep transport and time injectable for deterministic E2E tests.
- Keep unit selection logic isolated in `DispatchEngine` for future strategy upgrades.
- Keep channel contracts stable and explicit (see `docs/COMMUNICATION_PROTOCOL.md`).

## Where to Look First in Code

- `src/vehicle_agent/agent.py` - vehicle state machine and tick loop
- `src/orchestrator/agent.py` - central event handling and orchestration
- `src/orchestrator/emergency_service.py` - lifecycle/timeouts/duration policy
- `src/orchestrator/dispatch_engine.py` - selection, ETA, role assignment
- `src/orchestrator/persistence.py` - telemetry/alert/analytics persistence adapters

## Related Docs

- `docs/COMMUNICATION_PROTOCOL.md`
- `docs/DATA_ARCHITECTURE.md`
- `docs/SIMULATION.md`
- `docs/FAILURE_ACTIVATION_API.md`
- `docs/ROADMAP.md`
