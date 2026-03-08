# Failure Activation API

**Version:** 2.1.0  
**Last Updated:** 2026-03-08

This document explains how failures are activated, applied, and cleared in vehicle simulation.

## Supported Failure Scenarios

Defined by `FailureScenario` in `src/models/enums.py`:

- `ENGINE_OVERHEAT`
- `BATTERY_DEGRADATION`
- `FUEL_LEAK`
- `OIL_PRESSURE_DROP`
- `VIBRATION_ANOMALY`
- `BRAKE_DEGRADATION`

## Programmatic Activation

```python
from src.models.enums import FailureScenario
from src.vehicle_agent.agent import VehicleAgent

agent: VehicleAgent = ...

# Activate one scenario
agent.failure_injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

# Deactivate one scenario
agent.failure_injector.deactivate_scenario(FailureScenario.ENGINE_OVERHEAT)
```

## Runtime Semantics

- Activation stores the scenario with an activation timestamp.
- On each tick, `FailureInjector.apply_failures(...)` mutates telemetry according to elapsed time.
- Mutations are based on vehicle-type baselines (`src/vehicle_agent/config.py`) to avoid unrealistic uniform behavior.
- Scenarios are cumulative: multiple active scenarios can alter multiple sensors in the same tick.

## Interaction with Alerting and Maintenance

- Failures are applied before anomaly analysis.
- Alerts are generated from the mutated telemetry, not baseline telemetry.
- Critical alerts with active failures can transition the vehicle into `MAINTENANCE`.
- After repair completes, the agent deactivates all active scenarios and publishes an `alerts_cleared` event.

## Common Usage Patterns

### Inject one deterministic scenario for tests

- Activate exactly one scenario at test setup.
- Advance time/ticks.
- Assert expected telemetry drift and alert severity.

### Simulate compound degradation

- Activate two or more scenarios.
- Validate combined impact and maintenance behavior.

### Recovery flow validation

- Force critical condition.
- Assert `MAINTENANCE` status.
- Advance repair timer and assert:
  - status returns to `IDLE`,
  - `alerts_cleared` message is published,
  - orchestrator clears `has_active_alert` and can re-dispatch vehicle.

## References

- `src/vehicle_agent/failure_injector.py`
- `src/vehicle_agent/agent.py`
- `src/vehicle_agent/failure_scheduler.py`
- `tests/e2e/test_maintenance_retry.py`
