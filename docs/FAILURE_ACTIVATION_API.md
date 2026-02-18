# Failure Activation API - Phase 2

**Project AEGIS - Vehicle Digital Twin System**

This document describes how to programmatically activate failure scenarios for testing and demonstration purposes.

---

## Overview

The `FailureInjector` class allows you to simulate realistic vehicle failures during runtime. Each failure evolves over time based on documented progression rates from `docs/SIMULATION.md`.

---

## Available Failure Scenarios

```python
from src.models.enums import FailureScenario

FailureScenario.ENGINE_OVERHEAT        # Engine temperature increases by +2°C/min
FailureScenario.ALTERNATOR_FAILURE     # Voltage drops by -0.1V per 5min
FailureScenario.BRAKE_PAD_WEAR_CRITICAL  # Brake pads wear at 0.05mm/min
FailureScenario.TIRE_PRESSURE_LOW      # Tire pressure drops by -2 psi/min
```

---

## Basic Usage

### Accessing the Failure Injector

If you have access to a `VehicleAgent` instance:

```python
from src.vehicle_agent import VehicleAgent
from src.models.enums import FailureScenario

# Get the agent's failure injector
agent = VehicleAgent(config)
injector = agent.failure_injector

# Activate a failure
injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)

# Deactivate a failure
injector.deactivate_scenario(FailureScenario.ENGINE_OVERHEAT)
```

### Standalone Usage

For testing or manual control:

```python
from src.vehicle_agent.failure_injector import FailureInjector
from src.models.enums import FailureScenario

injector = FailureInjector()

# Activate multiple failures
injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)
injector.activate_scenario(FailureScenario.ALTERNATOR_FAILURE)

# Check active scenarios
print(injector.active_scenarios)  # {FailureScenario.ENGINE_OVERHEAT: datetime(...), ...}

# Get elapsed time since activation (seconds)
elapsed = injector.get_time_since_activation(FailureScenario.ENGINE_OVERHEAT)
print(f"Engine has been overheating for {elapsed:.1f} seconds")
```

---

## Failure Progression Details

### 1. Engine Overheat (`ENGINE_OVERHEAT`)

**Progression:**
- **Rate:** +2.0°C per minute
- **WARNING threshold:** 105°C (reached at ~15 minutes from 90°C baseline)
- **CRITICAL threshold:** 120°C (reached at ~25 minutes)

**Affected telemetry:**
- `engine_temp_celsius` increases linearly
- `coolant_temp_celsius` follows engine temp with slight delay

**Alert triggered:**
- WARNING: "Reduce RPM and monitor temperature. Schedule inspection within 4 hours."
- CRITICAL: "STOP IMMEDIATELY - Engine damage imminent. Activate limp mode."

---

### 2. Alternator Failure (`ALTERNATOR_FAILURE`)

**Progression:**
- **Voltage rate:** -0.1V per 5 minutes (-0.02V/min)
- **Battery drain:** -3% per minute
- **WARNING threshold:** 13.5V (reached at ~35 minutes from 14.2V baseline)
- **CRITICAL threshold:** 13.0V (reached at ~60 minutes)

**Affected telemetry:**
- `alternator_voltage` decreases linearly
- `battery_state_of_charge_percent` drains faster

**Alert triggered:**
- WARNING: "Alternator output low - Schedule inspection within 12 hours."
- CRITICAL: "Alternator not charging - Battery will drain. Replace alternator within 2 hours."

---

### 3. Brake Pad Wear (`BRAKE_PAD_WEAR_CRITICAL`)

**Progression:**
- **Wear rate:** 0.05mm per minute
- **Front pad multiplier:** 1.3x faster wear (0.065mm/min)
- **WARNING threshold:** 3.0mm (reached at ~100 minutes from 8mm baseline)
- **CRITICAL threshold:** 1.5mm (reached at ~130 minutes)

**Affected telemetry:**
- `brake_pad_thickness_mm` (all four wheels)
- Front pads (`front_left`, `front_right`) wear 30% faster

**Alert triggered:**
- WARNING: "front_left brake pad at 2.5mm - Schedule replacement within 48 hours."
- CRITICAL: "CRITICAL: front_left brake pad at 1.2mm - Replace immediately (metal-on-metal imminent)."

---

### 4. Tire Pressure Low (`TIRE_PRESSURE_LOW`)

**Progression:**
- **Pressure drop:** -2.0 psi per minute
- **WARNING threshold:** 60 psi (reached at ~10 minutes from 80 psi baseline)
- **CRITICAL threshold:** 40 psi (reached at ~20 minutes)

**Affected telemetry:**
- `tire_pressure_psi` (front_left tire only for single failure)

**Alert triggered:**
- WARNING: "front_left tire pressure low at 55.0 psi - Inspect for leak and refill."
- CRITICAL: "CRITICAL: front_left tire at 35.0 psi - Stop and replace immediately."

---

## Testing Example: Activate Failure During Simulation

```python
import asyncio
from src.vehicle_agent import VehicleAgent, AgentConfig
from src.models.enums import VehicleType, FailureScenario

async def test_engine_failure():
    # Create agent
    config = AgentConfig(
        vehicle_id="AMB-001",
        vehicle_type=VehicleType.AMBULANCE,
        telemetry_frequency=1.0  # 1 Hz
    )
    agent = VehicleAgent(config)
    
    # Connect to Redis
    await agent.redis_client.connect()
    
    # Run normally for 30 seconds
    for _ in range(30):
        await agent._tick()
        await asyncio.sleep(1)
    
    # Activate engine overheat
    print("🔥 Activating ENGINE_OVERHEAT scenario...")
    agent.failure_injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)
    
    # Continue running - temperature will increase
    # WARNING alert expected at ~15 minutes (900 seconds)
    # CRITICAL alert expected at ~25 minutes (1500 seconds)
    for _ in range(1800):  # 30 minutes
        await agent._tick()
        await asyncio.sleep(1)
    
    await agent.redis_client.disconnect()

# Run the test
asyncio.run(test_engine_failure())
```

---

## Demo Scenario: Multiple Cascading Failures

Simulate a worst-case scenario with multiple simultaneous failures:

```python
import asyncio
from datetime import timedelta

async def catastrophic_failure_demo(agent):
    """Simulate cascading failures over 30 minutes."""
    
    # Minute 0: Engine starts overheating
    agent.failure_injector.activate_scenario(FailureScenario.ENGINE_OVERHEAT)
    print("0:00 - Engine overheating begins")
    await asyncio.sleep(300)  # 5 minutes
    
    # Minute 5: Alternator fails (electrical system stressed)
    agent.failure_injector.activate_scenario(FailureScenario.ALTERNATOR_FAILURE)
    print("5:00 - Alternator failure detected")
    await asyncio.sleep(300)  # 5 minutes
    
    # Minute 10: Tire starts losing pressure (road hazard)
    agent.failure_injector.activate_scenario(FailureScenario.TIRE_PRESSURE_LOW)
    print("10:00 - Tire pressure leak starts")
    await asyncio.sleep(600)  # 10 minutes
    
    # Minute 20: Brake pads critically worn (heavy braking due to tire issue)
    agent.failure_injector.activate_scenario(FailureScenario.BRAKE_PAD_WEAR_CRITICAL)
    print("20:00 - Brake pad wear accelerates")
    await asyncio.sleep(600)  # 10 minutes
    
    # Minute 30: All systems failing
    print("30:00 - Multiple CRITICAL alerts expected")
    print("Vehicle should be flagged as unsafe to operate")
```

---

## Integration with Redis

Failure scenarios automatically affect telemetry published to Redis:

```bash
# Terminal 1: Start Redis
docker run -p 6379:6379 redis:7-alpine

# Terminal 2: Monitor telemetry channel
redis-cli SUBSCRIBE "aegis:fleet01:telemetry:AMB-001"

# Terminal 3: Monitor alerts channel
redis-cli SUBSCRIBE "aegis:fleet01:alerts:AMB-001"

# Terminal 4: Start vehicle with failure
uv run aegis-vehicle --vehicle-id AMB-001 --vehicle-type ambulance
```

---

## Expected Alert Timeline (ENGINE_OVERHEAT Example)

| Time | Temp (°C) | Event |
|------|-----------|-------|
| 0:00 | 90.0 | Failure activated |
| 5:00 | 100.0 | Temperature rising |
| 7:30 | 105.0 | ⚠️ WARNING alert generated |
| 15:00 | 120.0 | 🚨 CRITICAL alert generated |
| 15:00+ | Capped | Max temp reached, vehicle unsafe |

---

## API Reference

### `FailureInjector.activate_scenario(scenario: FailureScenario)`
Activates a failure scenario. Records activation timestamp for time-based progression.

### `FailureInjector.deactivate_scenario(scenario: FailureScenario)`
Deactivates a failure scenario. Telemetry will return to normal values.

### `FailureInjector.get_time_since_activation(scenario: FailureScenario) -> float`
Returns seconds elapsed since scenario was activated. Returns 0.0 if not active.

### `FailureInjector.apply_failures(telemetry: VehicleTelemetry) -> VehicleTelemetry`
Applies all active failure scenarios to telemetry. Returns a **new** telemetry object (immutable).

---

## Notes

- **Immutability**: `apply_failures()` returns a new telemetry object; the original is unchanged
- **Time-based**: Failures progress based on elapsed time since activation, not tick count
- **Multiple failures**: Can activate multiple scenarios simultaneously (they compound effects)
- **Alert generation**: Anomaly detector runs automatically after failure injection in `VehicleAgent._tick()`
- **No persistence**: Failures reset when agent restarts (by design for POC)

---

## Related Documentation

- `docs/SIMULATION.md` - Full failure scenario specifications and timelines
- `docs/DATA_ARCHITECTURE.md` - Telemetry field definitions
- `docs/COMMUNICATION_PROTOCOL.md` - Redis message formats
- `tests/unit/vehicle_agent/test_failure_injector.py` - Test examples

---

**Last Updated:** Phase 2 Completion (72 tests passing, 82.63% coverage)
