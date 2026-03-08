# Data Architecture - Project AEGIS

**Version:** 2.1.0  
**Status:** Implemented and active in runtime  
**Last Updated:** 2026-03-08

## Overview

AEGIS data architecture is optimized for real-time dispatch decisions:

- in-memory state is the operational source of truth,
- pub/sub messages carry canonical domain payloads,
- database persistence is asynchronous and analytics-focused.

This split keeps emergency coordination responsive while still preserving history.

## Data Ownership by Layer

### Runtime state (authoritative for control decisions)

- Fleet state: `FleetService.fleet` (`dict[str, VehicleStatusSnapshot]`).
- Active alerts: `FleetService.active_alerts` (`dict[str, PredictiveAlert]`).
- Emergency state: `EmergencyService.emergencies` (`dict[str, Emergency]`).
- Dispatch state: `EmergencyService.dispatches` (`dict[str, Dispatch]`).

These structures are updated directly from message events and API commands.

### Persistence state (durable history / analytics)

- Telemetry time-series persisted by `DatabaseTelemetryPersister`.
- Predictive alerts persisted by `DatabaseAlertPersister`.
- Dispatch snapshots + timeline events persisted by `DatabaseEmergencyAnalyticsPersister`.

Persistence failures are logged and do not block control-loop progression.

## Core Domain Models and Why They Matter

### Vehicle and telemetry domain

- `VehicleTelemetry` (`src/models/telemetry.py`)
  - Per-tick sensor payload.
  - Includes `vehicle_type` to avoid string-prefix inference.
  - Optionally carries `operational_status` so orchestrator can reflect true runtime transitions.
- `VehicleStatusSnapshot` (`src/models/dispatch.py`)
  - Orchestrator-maintained projection of each vehicle.
  - `is_available` is derived (`IDLE` and no active alert).

### Alert domain

- `PredictiveAlert` (`src/models/alerts.py`)
  - Actionable alert envelope with severity/category/probability/confidence.
  - Used for dispatch eligibility (`has_active_alert`) and ops visibility.

### Emergency/dispatch domain

- `Emergency` (`src/models/emergency.py`)
  - Incident lifecycle state machine (`PENDING -> DISPATCHING -> DISPATCHED -> IN_PROGRESS -> CLOSED`).
  - Captures severity, unit requirements, and coordination checkpoints.
- `Dispatch` + `DispatchedUnit` (`src/models/dispatch.py`)
  - Assignment record per emergency.
  - Tracks ack status, ETA estimates, and actual arrival timestamps.

### Event envelope domain

- `VehicleRegistrationEvent` (`src/models/events.py`)
  - Explicit startup metadata event (`event + payload`) for clean registration semantics.

## Data Flow: From Telemetry to Decision

1. Vehicle publishes `VehicleTelemetry`.
2. Orchestrator validates payload with Pydantic model parsing.
3. `FleetService.process_telemetry` updates `VehicleStatusSnapshot` fields.
4. Updated snapshot becomes immediately usable by `DispatchEngine`.
5. Same telemetry is enqueued for DB persistence asynchronously.

This is a projection pattern: write once to in-memory operational state, persist side effects out-of-band.

## Emergency Lifecycle Data Transitions

1. Emergency creation stores `Emergency` in `emergencies` map.
2. `DispatchEngine.select_units` creates `Dispatch` and mutates selected snapshots to `EN_ROUTE`.
3. Vehicle dispatch acknowledgments update `DispatchedUnit.acknowledged*` fields.
4. Vehicle arrival updates `actual_arrival_at` and computed `eta_error_minutes`.
5. Coordination tasks update `Emergency.coordination_status`.
6. Resolve/dismiss transitions set terminal timestamps and release units to `IDLE`.

## Machine Learning Artifacts

- Training data split: 80% is used for model training; the newest 20% is used by `HistoricalCrimeInjector` as holdout validation events.
- Serialized model artifact: running `src/ml/train_crime.py` persists a Random Forest model to `src/ml/crime_model.joblib` for orchestrator prediction runtime.

## Timing and Determinism Rules

- All default model timestamps are UTC-aware datetimes.
- Runtime loops and timeouts read from `Clock` abstraction, not direct `datetime.now` calls in control paths.
- `FastForwardClock` supports deterministic testing of long-duration workflows without wall-clock waiting.

## Channel Payload Contract Strategy

- Messages are serialized Pydantic model JSON (no extra transport envelope).
- Channel names encode routing context (`fleet_id`, `vehicle_id`, `emergency_id`).
- Payload schemas stay stable while transport remains replaceable (`RedisMessageBus` vs `InMemoryMessageBus`).

See `docs/COMMUNICATION_PROTOCOL.md` for exact channel/payload examples.

## Practical Guidance for Contributors

- When adding new telemetry metrics, update both:
  - `VehicleTelemetry` (ingress contract),
  - `VehicleStatusSnapshot` (dispatch/read model if metric is decision-relevant).
- Keep dispatch decision inputs inside in-memory snapshot fields.
- Keep DB persistence adapters side-effect only; avoid coupling dispatch outcomes to DB writes.
- Preserve backward compatibility for channel payload fields when possible.
