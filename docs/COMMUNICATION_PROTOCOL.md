# Communication Protocol - Project AEGIS

**Version:** 2.1.0  
**Protocol:** Pub/Sub via `MessageBus` abstraction  
**Runtime Transport:** Redis (`RedisMessageBus`)  
**Test Transport:** In-memory (`InMemoryMessageBus`)  
**Message Format:** JSON-serialized Pydantic models  
**Last Updated:** 2026-03-08

## Purpose

This document defines the **message contract** between vehicle agents and the orchestrator.

It is intentionally channel-driven and lightweight:

- channels encode routing context,
- payloads carry typed domain data,
- transport can change without changing payload contracts.

## Channel Taxonomy

### Vehicle -> Orchestrator

- `aegis:{fleet_id}:vehicles:register`
  - One-time startup metadata event (`VehicleRegistrationEvent`).
- `aegis:{fleet_id}:telemetry:{vehicle_id}`
  - High-frequency telemetry stream (`VehicleTelemetry`).
- `aegis:{fleet_id}:alerts:{vehicle_id}`
  - Predictive maintenance events (`PredictiveAlert`).
- `aegis:{fleet_id}:alerts_cleared:{vehicle_id}`
  - Maintenance completion signal (small JSON object with `vehicle_id`).
- `aegis:dispatch:{emergency_id}:ack`
  - Dispatch acknowledgment from unit (`vehicle_id`, `dispatch_id`, `acknowledged_at`).

### Orchestrator -> Vehicle

- `aegis:{fleet_id}:commands:{vehicle_id}`
  - Per-unit command channel (`dispatch` command payloads).
- `aegis:dispatch:{emergency_id}:resolved`
  - Broadcast resolution signal (`resolve` command + released vehicles).
- `aegis:dispatch:{emergency_id}:dismissed`
  - Broadcast dismissal signal for timeout-closed incidents.

### Orchestrator internal subscription patterns

- `aegis:*:vehicles:register`
- `aegis:*:telemetry:*`
- `aegis:*:alerts:*`
- `aegis:*:alerts_cleared:*`
- `aegis:dispatch:*:ack`

## Payload Contracts

### 1) Vehicle registration event

Channel example:

`aegis:fleet01:vehicles:register`

Model:

- `src/models/events.py` -> `VehicleRegistrationEvent`
- `src/models/vehicle.py` -> nested `VehicleRegistration`

```json
{
  "event": "vehicle.registered",
  "payload": {
    "vehicle_id": "AMB-001",
    "vehicle_type": "ambulance",
    "fleet_id": "fleet01",
    "operational_status": "idle",
    "timestamp": "2026-03-08T00:00:00Z"
  }
}
```

### 2) Telemetry event

Channel example:

`aegis:fleet01:telemetry:AMB-001`

Model:

- `src/models/telemetry.py` -> `VehicleTelemetry`

```json
{
  "vehicle_id": "AMB-001",
  "vehicle_type": "ambulance",
  "timestamp": "2026-03-08T00:00:01Z",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "speed_kmh": 40.0,
  "odometer_km": 1234.5,
  "engine_temp_celsius": 89.2,
  "battery_voltage": 13.7,
  "fuel_level_percent": 74.5,
  "oil_pressure_bar": 3.2,
  "vibration_ms2": 0.9,
  "brake_pad_mm": 11.3,
  "operational_status": "en_route"
}
```

### 3) Predictive alert event

Channel example:

`aegis:fleet01:alerts:AMB-001`

Model:

- `src/models/alerts.py` -> `PredictiveAlert`

Key fields consumed by orchestrator:

- `vehicle_id`
- `severity`
- `category`
- `component`
- `safe_to_operate`

### 4) Dispatch command

Channel example:

`aegis:fleet01:commands:AMB-001`

```json
{
  "command": "dispatch",
  "emergency_id": "2da5c2b7-7e34-4ee4-a020-ff33e274f530",
  "emergency_type": "medical",
  "location": {
    "latitude": 37.779,
    "longitude": -122.41
  },
  "dispatch_id": "f2f09bd6-54e6-4ca0-8d8f-3d645fbcd167",
  "role": "triage",
  "estimated_eta_minutes": 4.75
}
```

### 5) Dispatch acknowledgment

Channel example:

`aegis:dispatch:2da5c2b7-7e34-4ee4-a020-ff33e274f530:ack`

```json
{
  "vehicle_id": "AMB-001",
  "emergency_id": "2da5c2b7-7e34-4ee4-a020-ff33e274f530",
  "dispatch_id": "f2f09bd6-54e6-4ca0-8d8f-3d645fbcd167",
  "acknowledged_at": "2026-03-08T00:00:02Z"
}
```

### 6) Resolve broadcast

Channel pattern:

`aegis:dispatch:{emergency_id}:resolved`

```json
{
  "command": "resolve",
  "emergency_id": "2da5c2b7-7e34-4ee4-a020-ff33e274f530",
  "released_vehicles": ["AMB-001", "FIRE-001"]
}
```

### 7) Alert cleared notification

Channel example:

`aegis:fleet01:alerts_cleared:AMB-001`

```json
{
  "vehicle_id": "AMB-001",
  "cleared_at": "2026-03-08T00:10:00Z"
}
```

## Processing Semantics

- Orchestrator parses all incoming payloads into model objects before mutation.
- Invalid or malformed payloads are dropped with structured warning logs.
- Orchestrator state updates happen before async persistence side effects.
- Dispatch acks are matched by both `emergency_id` and `dispatch_id` to avoid stale updates.

## Contract Invariants

- Registration should occur before first telemetry from a vehicle process.
- `dispatch` payloads must include `dispatch_id` for ack tracking.
- Resolution payloads must include `command: "resolve"`.
- All timestamps are UTC ISO-8601.
- Vehicle identifiers are stable across all channel families.

## Backward Compatibility Guidance

- Add fields in payloads as optional first.
- Do not rename/remove existing required keys without coordinated rollout.
- Preserve channel patterns; add new channels instead of overloading existing semantics.
- Keep command values explicit (`dispatch`, `resolve`, `dismiss`) rather than inferred by channel alone.

## Related Docs

- `docs/ARCHITECTURE.md`
- `docs/DATA_ARCHITECTURE.md`
- `docs/SIMULATION.md`
