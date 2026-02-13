# Communication Protocol - Project AEGIS

**Version:** 1.0.0  
**Protocol:** Redis Pub/Sub (Phase 1), MQTT (Phase 2)  
**Message Format:** JSON

---

## 🔌 Redis Channel Architecture

### Channel Naming Convention

```
aegis:{fleet_id}:{component}:{vehicle_id}:{message_type}
```

**Pattern Components:**
- `aegis` - System prefix
- `{fleet_id}` - Fleet identifier (e.g., "fleet01", "sf_central")
- `{component}` - System component (telemetry, alerts, commands, etc.)
- `{vehicle_id}` - Vehicle identifier (e.g., "AMB-001") or "broadcast"
- `{message_type}` - Optional message subtype

---

## 📡 Channel Definitions

### **Vehicle → Orchestrator Channels**

#### 1. Telemetry Stream (High Frequency)
```
Channel: aegis:fleet01:telemetry:{vehicle_id}
Frequency: 1 Hz (every second)
Retention: None (stream only)
Priority: NORMAL
```

**Payload:**
```json
{
  "message_id": "550e8400-e29b-41d4-a716-446655440000",
  "message_type": "telemetry.update",
  "timestamp": "2026-02-10T14:32:01.000Z",
  "source": "AMB-001",
  "destination": "orchestrator",
  "priority": "normal",
  "payload": {
    "vehicle_id": "AMB-001",
    "timestamp": "2026-02-10T14:32:01.000Z",
    "sequence_number": 12345,
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "altitude": 15.5,
      "heading": 45.0,
      "speed_kmh": 65.5
    },
    "engine_temp_celsius": 92.5,
    "engine_rpm": 2500,
    "battery_voltage": 13.8,
    "fuel_level_percent": 75.0,
    "tire_pressure_psi": {
      "front_left": 80.0,
      "front_right": 80.0,
      "rear_left": 80.0,
      "rear_right": 80.0
    }
    // ... 35+ more telemetry fields
  }
}
```

---

#### 2. Heartbeat (Health Check)
```
Channel: aegis:fleet01:heartbeat:{vehicle_id}
Frequency: Every 10 seconds
Retention: Last value only (Redis hash)
Priority: HIGH
```

**Payload:**
```json
{
  "message_type": "vehicle.heartbeat",
  "timestamp": "2026-02-10T14:32:00.000Z",
  "source": "AMB-001",
  "payload": {
    "vehicle_id": "AMB-001",
    "uptime_seconds": 86400,
    "last_telemetry_sequence": 12345,
    "agent_version": "1.0.0",
    "system_health": {
      "cpu_percent": 15.5,
      "memory_percent": 42.3,
      "disk_percent": 58.1,
      "network_latency_ms": 12.5,
      "redis_connected": true
    }
  }
}
```

---

#### 3. Alert Generation
```
Channel: aegis:fleet01:alerts:{vehicle_id}
Frequency: On alert generation (event-driven)
Retention: 24 hours (Redis stream)
Priority: HIGH or CRITICAL
```

**Payload:**
```json
{
  "message_type": "alert.generated",
  "timestamp": "2026-02-10T14:32:15.000Z",
  "source": "AMB-001",
  "priority": "high",
  "payload": {
    "alert_id": "alert-550e8400",
    "vehicle_id": "AMB-001",
    "severity": "warning",
    "category": "electrical",
    "component": "alternator",
    "failure_probability": 0.75,
    "confidence": 0.88,
    "predicted_failure_min_hours": 8.0,
    "predicted_failure_max_hours": 24.0,
    "predicted_failure_likely_hours": 12.0,
    "can_complete_current_mission": true,
    "safe_to_operate": true,
    "recommended_action": "Schedule alternator inspection within 12 hours",
    "contributing_factors": [
      "battery_voltage declining trend",
      "alternator_voltage below 13.5V",
      "increased electrical load"
    ],
    "model_version": "1.0.0"
  }
}
```

---

#### 4. Status Change
```
Channel: aegis:fleet01:status:{vehicle_id}
Frequency: On status change (event-driven)
Retention: Last value only
Priority: NORMAL
```

**Payload:**
```json
{
  "message_type": "vehicle.status_change",
  "timestamp": "2026-02-10T14:32:00.000Z",
  "source": "AMB-001",
  "payload": {
    "vehicle_id": "AMB-001",
    "operational_status": "en_route",
    "previous_status": "idle",
    "mission_id": "MISSION-2026-02-10-001",
    "crew_count": 3,
    "destination": {
      "latitude": 37.8049,
      "longitude": -122.4194
    },
    "eta_seconds": 420
  }
}
```

---

#### 5. Local Decision Report
```
Channel: aegis:fleet01:decisions:{vehicle_id}
Frequency: On autonomous decision (event-driven)
Retention: 24 hours
Priority: HIGH
```

**Payload:**
```json
{
  "message_type": "vehicle.local_decision",
  "timestamp": "2026-02-10T14:32:00.000Z",
  "source": "AMB-001",
  "priority": "high",
  "payload": {
    "vehicle_id": "AMB-001",
    "decision_type": "limp_mode_activated",
    "reason": "Engine temperature exceeded 120°C",
    "telemetry_snapshot": {
      "engine_temp_celsius": 125.5,
      "coolant_temp_celsius": 118.0,
      "engine_rpm": 3500
    },
    "alert_ids": ["alert-550e8400"],
    "action_taken": "Reduced max RPM to 2000, activated hazard lights",
    "requires_orchestrator_override": false
  }
}
```

---

### **Orchestrator → Vehicle Channels**

#### 6. Commands
```
Channel: aegis:fleet01:commands:{vehicle_id}
Frequency: On demand (event-driven)
Retention: Until acknowledged
Priority: HIGH or CRITICAL
```

**Payload Examples:**

**Dispatch Command:**
```json
{
  "message_type": "vehicle.command",
  "timestamp": "2026-02-10T14:32:00.000Z",
  "source": "orchestrator",
  "destination": "AMB-001",
  "priority": "critical",
  "correlation_id": "cmd-550e8400",
  "payload": {
    "command_type": "dispatch",
    "parameters": {
      "mission_id": "MISSION-2026-02-10-001",
      "destination": {
        "latitude": 37.8049,
        "longitude": -122.4194,
        "address": "123 Emergency St, San Francisco, CA"
      },
      "priority": "life_threatening",
      "patient_count": 1,
      "special_equipment": ["defibrillator"]
    },
    "reason": "Cardiac arrest reported",
    "issued_by": "dispatcher_user_42",
    "requires_acknowledgment": true
  }
}
```

**Maintenance Mode Command:**
```json
{
  "message_type": "vehicle.command",
  "payload": {
    "command_type": "maintenance_mode",
    "parameters": {
      "duration_hours": 4,
      "maintenance_type": "scheduled",
      "garage_location": "STATION-01"
    },
    "reason": "Alternator replacement required",
    "issued_by": "fleet_manager"
  }
}
```

---

#### 7. Alert Acknowledgment
```
Channel: aegis:fleet01:commands:{vehicle_id}
Frequency: On alert processing
Priority: NORMAL
```

**Payload:**
```json
{
  "message_type": "alert.acknowledge",
  "timestamp": "2026-02-10T14:32:05.000Z",
  "source": "orchestrator",
  "destination": "AMB-001",
  "correlation_id": "alert-550e8400",
  "payload": {
    "alert_id": "alert-550e8400",
    "acknowledged_by": "orchestrator",
    "action_taken": "Maintenance scheduled for 2026-02-11 08:00",
    "override_recommendation": false
  }
}
```

---

#### 8. Broadcast Messages
```
Channel: aegis:fleet01:broadcast
Frequency: On demand
Retention: 5 minutes
Priority: Varies
```

**Payload Example (Configuration Update):**
```json
{
  "message_type": "vehicle.config_update",
  "timestamp": "2026-02-10T14:00:00.000Z",
  "source": "orchestrator",
  "destination": null,  // Broadcast to all
  "payload": {
    "config_key": "telemetry_frequency_hz",
    "config_value": 0.5,
    "reason": "Reduce network load during maintenance window",
    "effective_immediately": true,
    "duration_seconds": 3600
  }
}
```

---

### **Orchestrator → Dashboard Channels**

#### 9. Fleet Status Updates
```
Channel: aegis:fleet01:dashboard:fleet_status
Frequency: Every 5 seconds (aggregated)
Retention: None (WebSocket stream)
Priority: NORMAL
```

**Payload:**
```json
{
  "message_type": "fleet.status",
  "timestamp": "2026-02-10T14:32:00.000Z",
  "source": "orchestrator",
  "payload": {
    "fleet_id": "fleet01",
    "total_vehicles": 10,
    "status_summary": {
      "idle": 5,
      "en_route": 3,
      "on_scene": 1,
      "maintenance": 1,
      "offline": 0
    },
    "active_alerts": {
      "critical": 0,
      "warning": 2,
      "info": 5
    },
    "active_missions": 4,
    "average_response_time_seconds": 180
  }
}
```

---

#### 10. Dashboard Vehicle Updates
```
Channel: aegis:fleet01:dashboard:vehicle:{vehicle_id}
Frequency: 0.2 Hz (every 5 seconds, throttled)
Retention: None
Priority: LOW
```

**Payload (Simplified Telemetry):**
```json
{
  "message_type": "vehicle.update",
  "timestamp": "2026-02-10T14:32:00.000Z",
  "payload": {
    "vehicle_id": "AMB-001",
    "location": {
      "latitude": 37.7749,
      "longitude": -122.4194,
      "heading": 45.0
    },
    "operational_status": "en_route",
    "speed_kmh": 65.5,
    "health_score": 0.88,  // Aggregate health
    "active_alerts": 1,
    "mission_id": "MISSION-2026-02-10-001"
  }
}
```

---

## 📊 Redis Data Structures

### Pub/Sub Channels
Used for real-time streaming (telemetry, events).

```python
# Publishing
redis.publish("aegis:fleet01:telemetry:AMB-001", json.dumps(message))

# Subscribing
pubsub = redis.pubsub()
pubsub.subscribe("aegis:fleet01:telemetry:*")
for message in pubsub.listen():
    handle_telemetry(message)
```

---

### Streams (for Alert History)
Used for persistent event logs with consumer groups.

```python
# Add alert to stream
redis.xadd(
    "aegis:fleet01:alerts:AMB-001",
    {"alert_data": json.dumps(alert)},
    maxlen=1000  # Keep last 1000 alerts
)

# Read alert history
alerts = redis.xrange("aegis:fleet01:alerts:AMB-001", "-", "+", count=100)
```

---

### Hashes (for Current State)
Used for last known vehicle state (fast lookup).

```python
# Store current state
redis.hset(
    "aegis:fleet01:vehicle:AMB-001:state",
    mapping={
        "operational_status": "idle",
        "location": json.dumps({"lat": 37.7749, "lng": -122.4194}),
        "last_update": "2026-02-10T14:32:00.000Z"
    }
)

# Get current state
state = redis.hgetall("aegis:fleet01:vehicle:AMB-001:state")
```

---

### Sorted Sets (for Time-Based Queries)
Used for recent alerts with timestamp scoring.

```python
# Add alert with timestamp score
redis.zadd(
    "aegis:fleet01:recent_alerts",
    {alert_id: timestamp_score}
)

# Get alerts from last hour
one_hour_ago = time.time() - 3600
recent = redis.zrangebyscore(
    "aegis:fleet01:recent_alerts",
    one_hour_ago,
    "+inf"
)
```

---

## 🔄 Message Flow Examples

### Example 1: Vehicle Dispatch Flow
```
1. Orchestrator receives emergency call
2. Orchestrator → Vehicle (AMB-001)
   Channel: aegis:fleet01:commands:AMB-001
   Message: vehicle.command (dispatch)
   
3. Vehicle acknowledges command
   Vehicle → Orchestrator
   Channel: aegis:fleet01:status:AMB-001
   Message: vehicle.status_change (idle → en_route)
   
4. Vehicle streams telemetry during journey
   Vehicle → Orchestrator (every 1 second)
   Channel: aegis:fleet01:telemetry:AMB-001
   Message: telemetry.update
   
5. Orchestrator → Dashboard (every 5 seconds)
   Channel: WebSocket
   Message: vehicle.update (aggregated)
   
6. Vehicle arrives on scene
   Vehicle → Orchestrator
   Channel: aegis:fleet01:status:AMB-001
   Message: vehicle.status_change (en_route → on_scene)
```

---

### Example 2: Alert Generation & Response Flow
```
1. Vehicle detects anomaly (alternator voltage low)
   Local rule engine evaluates telemetry
   
2. Vehicle → Orchestrator
   Channel: aegis:fleet01:alerts:AMB-001
   Message: alert.generated (warning severity)
   
3. Orchestrator processes alert
   - Logs to TimescaleDB
   - Updates fleet state
   - Evaluates mission impact
   
4. Orchestrator → Vehicle
   Channel: aegis:fleet01:commands:AMB-001
   Message: alert.acknowledge
   
5. Orchestrator → Dashboard
   Channel: WebSocket
   Message: alert.broadcast (for UI notification)
   
6. If critical, Orchestrator → Vehicle
   Channel: aegis:fleet01:commands:AMB-001
   Message: vehicle.command (return_to_base or maintenance_mode)
```

---

## 🔐 Message Validation

All messages must pass validation:

1. **Schema Validation**: Pydantic models validate structure
2. **Timestamp Check**: Message not older than TTL
3. **Source Verification**: Source exists in fleet registry
4. **Sequence Ordering**: Telemetry sequence numbers must increment
5. **Correlation**: Response messages must have valid correlation_id

---

## 📈 Performance Characteristics

### Message Size
- Telemetry: ~2-3 KB (JSON)
- Heartbeat: ~500 bytes
- Alert: ~1-2 KB
- Command: ~500-1000 bytes

### Throughput (10 vehicles)
- Telemetry: 10 msg/sec (~30 KB/sec)
- Heartbeat: 1 msg/sec (~500 bytes/sec)
- Alerts: ~0.1 msg/sec (occasional)
- Commands: ~0.1 msg/sec (occasional)

**Total**: ~11 msg/sec, ~31 KB/sec

### Latency Targets
- Telemetry publish: <10ms
- Command delivery: <100ms
- Dashboard update: <500ms (including aggregation)

---

## 🔄 Future: MQTT Migration

When migrating to MQTT (Phase 2):

**Topic Mapping:**
```
Redis: aegis:fleet01:telemetry:AMB-001
MQTT:  aegis/fleet01/vehicle/AMB-001/telemetry

Redis: aegis:fleet01:commands:AMB-001
MQTT:  aegis/fleet01/vehicle/AMB-001/commands
```

**QoS Levels:**
- Telemetry: QoS 0 (at most once, fire and forget)
- Alerts: QoS 1 (at least once, acknowledged)
- Commands: QoS 2 (exactly once, assured delivery)

**Last Will Testament:**
```
Topic: aegis/fleet01/vehicle/AMB-001/lwt
Payload: {"status": "offline", "timestamp": "..."}
```

---

## 📚 Related Documentation

- [DATA_ARCHITECTURE.md](./DATA_ARCHITECTURE.md) - Data models
- [SIMULATION.md](./SIMULATION.md) - Failure scenarios
- [ROADMAP.md](./ROADMAP.md) - Implementation timeline

---

**Last Updated:** 2026-02-10
