# Simulation & Failure Scenarios - Project AEGIS

**Version:** 1.0.0  
**Purpose:** Realistic testing and ML training data generation

---

## 🎯 Overview

Project AEGIS uses **synthetic data generation** to simulate emergency vehicle behavior and failure modes. This enables:
1. Testing without real vehicles
2. Generating 30+ days of training data for ML models
3. Reproducing rare failure scenarios on demand
4. Validating alert detection logic

---

## 🚑 Vehicle Types & Specifications

### Ambulance (Type A: Box Ambulance)
**Base Specifications:**
- Chassis: Ford F-450 Super Duty
- Engine: 6.7L V8 Diesel
- Gross Vehicle Weight: 14,500 lbs
- Top Speed: 100 mph (limited to 80 mph operational)
- Fuel Capacity: 40 gallons (151 liters)

**Typical Operating Patterns:**
- Average daily mileage: 50-150 miles
- Missions per day: 8-15
- Average mission duration: 25-45 minutes
- Idle time at station: 40-60% of shift
- High-speed operation: 15-20% of active time

**Equipment:**
- Defibrillator (Zoll X Series)
- Ventilator (Philips Trilogy Evo)
- Stretcher (Stryker Power-PRO)
- Medical oxygen tanks (2x M-size cylinders)
- IV pumps, monitors, etc.

---

### Fire Truck (Type 1: Engine/Pumper)
**Base Specifications:**
- Chassis: Pierce Enforcer
- Engine: Detroit Diesel DD13 12.8L
- Gross Vehicle Weight: 42,000 lbs
- Water Tank: 500 gallons
- Pump Capacity: 1,500 GPM

**Typical Operating Patterns:**
- Average daily mileage: 20-80 miles
- Calls per day: 4-10
- Average call duration: 45-90 minutes
- Idle time at station: 60-75% of shift
- Pump operation: 10-20% of call time

**Equipment:**
- Water pump (1,500 GPM rated)
- Aerial ladder (75-foot)
- Foam system
- Generator (25 kW)
- Hydraulic rescue tools

---

## 📊 Telemetry Simulation Models

### Physics-Based Movement
Vehicles follow realistic physics:

```python
# Acceleration model
def calculate_acceleration(throttle_position, current_speed, vehicle_weight):
    """
    Realistic acceleration considering:
    - Throttle position (0-100%)
    - Current speed (air resistance increases with speed)
    - Vehicle weight (affects acceleration capability)
    """
    max_acceleration = 3.5  # m/s² for ambulance
    air_resistance_factor = 0.0001 * (current_speed ** 2)
    weight_penalty = vehicle_weight / 14500  # Normalized to ambulance
    
    return max_acceleration * (throttle_position / 100) * \
           (1 - air_resistance_factor) / weight_penalty
```

---

### Correlated Sensor Readings
Telemetry values are interdependent:

**Engine Temperature Model:**
```python
def simulate_engine_temp(rpm, ambient_temp, coolant_level, time_delta):
    """
    Engine temperature depends on:
    - RPM (higher RPM = more heat)
    - Ambient temperature
    - Coolant level (lower level = less cooling)
    - Time (heat builds gradually)
    """
    base_temp = 70.0  # Celsius at idle
    rpm_contribution = (rpm / 1000) * 8.0
    ambient_contribution = (ambient_temp - 20) * 0.5
    coolant_penalty = (100 - coolant_level) * 0.3
    
    target_temp = base_temp + rpm_contribution + \
                  ambient_contribution + coolant_penalty
    
    # Temperature changes gradually (thermal inertia)
    current_temp = smooth_approach(current_temp, target_temp, time_delta)
    return current_temp
```

**Battery Charge Model:**
```python
def simulate_battery(alternator_output, electrical_load, battery_capacity):
    """
    Battery state depends on:
    - Alternator output (charging)
    - Electrical load (discharge)
    - Battery health/capacity
    """
    net_current = alternator_output - electrical_load
    
    # Charge/discharge rate (simplified)
    charge_rate = net_current / battery_capacity
    new_soc = current_soc + (charge_rate * time_delta)
    
    # Voltage correlates with state of charge
    voltage = 11.5 + (new_soc / 100) * 2.5  # 11.5V empty, 14V full
    
    return new_soc, voltage
```

---

## 🔥 Failure Scenarios

### 1. Engine Failures

#### **Scenario: Engine Overheat**
**Trigger:** Coolant leak + extended high-speed operation

**Progression:**
```yaml
trigger_after_seconds: 300  # 5 minutes into mission
initial_coolant_level: 100%
leak_rate: 2% per minute
affected_metrics:
  - engine_temp_celsius: +2°C per minute
  - coolant_temp_celsius: +2.5°C per minute
  - coolant_level: -2% per minute

failure_threshold: 120°C
critical_threshold: 135°C

timeline:
  - t=0: Normal operation (engine_temp=90°C)
  - t=5min: Leak starts, subtle temperature rise
  - t=15min: Temp reaches 105°C (WARNING alert)
  - t=25min: Temp reaches 120°C (CRITICAL alert, limp mode)
  - t=30min: Temp reaches 135°C (engine damage imminent)
```

**Observable Patterns:**
- Steady temperature increase (linear trend)
- Coolant level dropping
- Engine RPM may spike (driver pushing harder)
- Reduced performance as safety systems engage

---

#### **Scenario: Oil Pressure Drop**
**Trigger:** Oil pump wear or leak

**Progression:**
```yaml
trigger_after_seconds: 600
initial_oil_pressure: 45 psi (normal at 2000 RPM)
degradation_rate: 1 psi per 2 minutes

affected_metrics:
  - oil_pressure_psi: -0.5 psi per minute
  - engine_temp_celsius: +0.5°C per minute (poor lubrication)
  - engine_noise_db: +2 dB per minute (optional metric)

failure_threshold: 20 psi
critical_threshold: 10 psi

timeline:
  - t=0: Normal (45 psi)
  - t=10min: Pressure drop begins
  - t=40min: 25 psi (WARNING)
  - t=50min: 20 psi (CRITICAL - engine damage risk)
  - t=54min: 10 psi (catastrophic failure imminent)
```

---

### 2. Electrical System Failures

#### **Scenario: Alternator Failure**
**Trigger:** Bearing wear, gradual failure

**Progression:**
```yaml
trigger_after_seconds: 1200
initial_alternator_output: 14.2V (normal)
degradation_rate: 0.1V per 5 minutes

affected_metrics:
  - alternator_voltage: decreases to battery voltage level
  - battery_soc: -3% per minute (discharging)
  - battery_voltage: correlates with SOC

failure_threshold: alternator_voltage < 13.5V
critical_threshold: battery_soc < 20%

timeline:
  - t=0: Normal charging (14.2V)
  - t=20min: Alternator starts failing (13.8V)
  - t=40min: 13.2V (WARNING - not charging properly)
  - t=60min: 12.8V (battery discharging)
  - t=90min: Battery SOC 20% (CRITICAL)
  - t=120min: Battery dead (vehicle inoperable)
```

**Observable Patterns:**
- Gradual voltage decline
- Battery SOC decreasing despite engine running
- Electrical load may be reduced by agent (turn off non-essentials)

---

#### **Scenario: Battery Degradation**
**Trigger:** Age, repeated deep discharges

**Progression:**
```yaml
# This is a slow scenario (days/weeks in real life, minutes in simulation)
trigger_after_seconds: 0  # Present from start
initial_battery_health: 85%
degradation_rate: 0.5% per hour

affected_metrics:
  - battery_health_percent: decreases over time
  - battery_capacity_ah: reduced proportionally
  - charging_efficiency: reduced

failure_threshold: battery_health < 60%
critical_threshold: battery_health < 40%

observable_effects:
  - Voltage drops faster under load
  - Slower recharge rate
  - Cannot hold charge overnight
  - Difficult cold starts (simulated ambient_temp < 0°C)
```

---

### 3. Brake System Failures

#### **Scenario: Brake Pad Wear (Critical)**
**Trigger:** Extended heavy braking, high mileage

**Progression:**
```yaml
trigger_after_seconds: 0  # Gradual over entire simulation
initial_pad_thickness:
  front_left: 8.0 mm
  front_right: 8.0 mm
  rear_left: 9.0 mm
  rear_right: 9.0 mm

wear_rate: 0.05 mm per heavy brake event
uneven_wear: front pads wear 30% faster

failure_threshold: 3.0 mm
critical_threshold: 1.5 mm

timeline:
  - t=0: Normal (8mm)
  - t=50 braking events: 5.5mm (INFO)
  - t=100 events: 3.5mm (WARNING)
  - t=110 events: 2.0mm (CRITICAL - immediate maintenance)
  - t=120 events: Metal-on-metal (catastrophic)
```

**Observable Patterns:**
- Gradual thickness reduction
- Uneven wear (one side wears faster)
- Increased brake temperature
- Longer stopping distances (simulated)

---

#### **Scenario: Brake Fluid Leak**
**Trigger:** Seal failure, line rupture

**Progression:**
```yaml
trigger_after_seconds: 800
initial_fluid_level: 100%
leak_rate: 5% per minute (slow leak)

affected_metrics:
  - brake_fluid_level: decreases
  - brake_pressure: reduced with fluid loss
  - brake_effectiveness: reduced

failure_threshold: 50% fluid level
critical_threshold: 25% fluid level

timeline:
  - t=0: Normal
  - t=13min: Leak starts
  - t=23min: 50% level (WARNING)
  - t=28min: 25% level (CRITICAL - brake failure risk)
  - t=33min: No brakes (catastrophic)
```

---

### 4. Tire Failures

#### **Scenario: Slow Tire Leak**
**Trigger:** Nail puncture, valve stem leak

**Progression:**
```yaml
trigger_after_seconds: 600
affected_tire: front_left
initial_pressure: 80 psi
leak_rate: 2 psi per minute

affected_metrics:
  - tire_pressure_psi[front_left]: decreases
  - vibration_g_force: increases as tire deflates
  - steering_pull: simulated (optional)

failure_threshold: 60 psi
critical_threshold: 40 psi

timeline:
  - t=0: Normal (80 psi)
  - t=10min: Leak starts
  - t=20min: 60 psi (WARNING)
  - t=30min: 40 psi (CRITICAL - unsafe to drive)
  - t=40min: 0 psi (blowout/flat)
```

---

#### **Scenario: Sudden Tire Blowout**
**Trigger:** Random event, road hazard, overload

**Progression:**
```yaml
trigger_after_seconds: RANDOM(300, 1800)
affected_tire: RANDOM(front_left, front_right, rear_left, rear_right)
failure_mode: catastrophic (instant)

timeline:
  - t=0: Normal (80 psi)
  - t=random: Instant drop to 0 psi
  - immediate effects:
      - pressure = 0 psi
      - vibration spikes
      - speed reduction (safety)
      - hazard lights activate
      - vehicle slows to safe stop
```

---

### 5. Fuel System Failures

#### **Scenario: Fuel Pump Failure**
**Trigger:** Electrical failure, wear

**Progression:**
```yaml
trigger_after_seconds: 900
failure_mode: intermittent → complete

affected_metrics:
  - fuel_pressure: fluctuates then drops
  - engine_rpm: fluctuates (fuel starvation)
  - engine_performance: reduced

timeline:
  - t=0: Normal
  - t=15min: Intermittent fuel pressure drops (WARNING)
  - t=25min: Frequent pressure drops (CRITICAL)
  - t=30min: Complete pump failure (engine stalls)
```

---

### 6. Equipment Failures (Type-Specific)

#### **Fire Truck: Water Pump Failure**
```yaml
trigger_after_seconds: 600
trigger_condition: pump_active == true

affected_metrics:
  - pump_pressure_psi: decreases
  - pump_flow_gpm: decreases
  - pump_temperature: increases (bearing failure)

failure_threshold: flow < 1000 GPM (rated 1500)
critical_threshold: flow < 500 GPM

timeline:
  - t=0: Pump activated (1500 GPM, normal)
  - t=10min: Performance degrades (1200 GPM, WARNING)
  - t=20min: Significant loss (800 GPM, CRITICAL)
  - t=25min: Pump seizes (0 GPM)
```

---

#### **Ambulance: Defibrillator Battery Low**
```yaml
trigger_after_seconds: 0  # Starts low
initial_battery: 25%
discharge_rate: 1% per minute (on standby)
discharge_rate_active: 10% per use

failure_threshold: 20%
critical_threshold: 10%

timeline:
  - t=0: 25% (WARNING at start)
  - t=5min: 20% (repeated warnings)
  - t=10min: 15% (CRITICAL)
  - t=15min: 10% (equipment unusable soon)
  - t=18min: 0% (non-functional)
```

---

## 🎲 Randomness & Realism

### Noise Injection
All telemetry includes realistic noise:

```python
def add_sensor_noise(value, noise_level=0.02):
    """Add gaussian noise to sensor readings"""
    noise = random.gauss(0, noise_level * value)
    return value + noise

# Example: Engine temp 90°C ± 1.8°C noise
engine_temp = add_sensor_noise(90.0, noise_level=0.02)
# Result: 88.5°C to 91.5°C (random each reading)
```

---

### Environmental Factors

**Weather Conditions:**
```python
weather_effects = {
    "clear": {
        "ambient_temp": 20,
        "humidity": 50,
        "road_friction": 1.0
    },
    "rain": {
        "ambient_temp": 15,
        "humidity": 85,
        "road_friction": 0.7,  # Affects braking
        "visibility": 0.6
    },
    "snow": {
        "ambient_temp": -5,
        "humidity": 70,
        "road_friction": 0.4,
        "battery_efficiency": 0.7,  # Cold affects battery
        "engine_warmup_time": 300  # 5 min longer
    },
    "extreme_heat": {
        "ambient_temp": 40,
        "humidity": 30,
        "engine_temp_offset": +10,  # Runs hotter
        "ac_load": 2000  # W (extra electrical load)
    }
}
```

---

### Mission Patterns

**Ambulance Mission Simulation:**
```python
class AmbulanceMission:
    def __init__(self):
        self.phases = [
            "dispatch",       # Receive call, prepare
            "en_route",       # High-speed response
            "on_scene",       # Patient care, idle engine
            "transport",      # Return with patient (smoother driving)
            "at_hospital",    # Handoff, idle
            "return_to_base"  # Return to station
        ]
        
        self.phase_durations = {
            "dispatch": (30, 120),        # 30s-2min
            "en_route": (180, 900),       # 3-15min
            "on_scene": (300, 1800),      # 5-30min
            "transport": (300, 1200),     # 5-20min
            "at_hospital": (180, 600),    # 3-10min
            "return_to_base": (300, 900)  # 5-15min
        }
        
        self.phase_characteristics = {
            "en_route": {
                "siren_active": True,
                "lights_active": True,
                "avg_speed": 70,  # km/h
                "acceleration": "aggressive"
            },
            "on_scene": {
                "engine_idle": True,
                "equipment_active": ["defibrillator", "ventilator"],
                "electrical_load": "high"
            },
            "transport": {
                "siren_active": False,  # Usually
                "lights_active": True,
                "avg_speed": 50,
                "acceleration": "smooth"  # Patient comfort
            }
        }
```

---

## 🧪 Simulation Configuration

### Simulation Profiles

**Profile 1: Normal Operation (80% of time)**
```yaml
failure_probability: 0.0
mission_frequency: 2 per hour (ambulance), 0.5 per hour (fire truck)
weather: clear
traffic: normal
crew_fatigue: false
```

**Profile 2: Stress Test (10% of time)**
```yaml
failure_probability: 0.15
mission_frequency: 5 per hour
weather: rain or extreme_heat
traffic: heavy
multiple_simultaneous_missions: true
```

**Profile 3: Failure Focused (10% of time)**
```yaml
failure_probability: 0.8
inject_specific_scenarios: true
scenarios:
  - engine_overheat
  - alternator_failure
  - brake_pad_critical
mission_frequency: normal
```

---

### Generating Training Datasets

**30-Day Dataset Generation:**
```python
simulation_config = {
    "duration_days": 30,
    "num_vehicles": {
        "ambulance": 6,
        "fire_truck": 4
    },
    "telemetry_frequency_hz": 1.0,
    "failure_scenarios": [
        {"scenario": "engine_overheat", "probability": 0.02},
        {"scenario": "alternator_failure", "probability": 0.03},
        {"scenario": "battery_degradation", "probability": 0.10},
        {"scenario": "brake_pad_wear", "probability": 0.15},
        {"scenario": "tire_leak", "probability": 0.05},
        # ... all 16 scenarios
    ],
    "weather_distribution": {
        "clear": 0.60,
        "rain": 0.25,
        "snow": 0.10,
        "extreme_heat": 0.05
    }
}

# Expected output:
# - 10 vehicles × 30 days × 86,400 seconds = 25.9 million telemetry records
# - ~200-300 failure events (varying severity)
# - ~500-800 missions simulated
# - ~80 GB raw data (compressed: ~20 GB)
```

---

## 📈 Validation Metrics

To ensure simulation realism:

1. **Statistical Validation:**
   - Sensor values within expected ranges (99.9% of time)
   - Failure rates match real-world data (if available)
   - Mission durations follow expected distributions

2. **Correlation Validation:**
   - Engine temp correlates with RPM (r > 0.7)
   - Battery SOC correlates with voltage (r > 0.9)
   - Speed correlates with fuel consumption (r > 0.6)

3. **Physics Validation:**
   - Acceleration/deceleration within vehicle capabilities
   - Fuel consumption matches expected MPG
   - GPS coordinates follow valid paths

---

## 🔧 Implementation Tools

**Required Libraries:**
```python
# Simulation
numpy  # Random distributions, calculations
scipy  # Physics models
faker  # Realistic IDs, names

# Data generation
pandas  # DataFrame management
pyarrow  # Parquet export

# Physics
pint  # Unit conversions (mph→km/h, etc.)
```

---

## 📚 Related Documentation

- [DATA_ARCHITECTURE.md](./DATA_ARCHITECTURE.md) - Data models
- [COMMUNICATION_PROTOCOL.md](./COMMUNICATION_PROTOCOL.md) - Message formats
- [ROADMAP.md](./ROADMAP.md) - Implementation timeline

---

**Last Updated:** 2026-02-10
