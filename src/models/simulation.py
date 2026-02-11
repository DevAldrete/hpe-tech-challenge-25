"""
Simulation configuration and failure scenario models for Project AEGIS.

This module contains data structures for configuring realistic vehicle simulations.
"""

from pydantic import BaseModel, Field

from .enums import FailureScenario, VehicleType


class ScenarioParameters(BaseModel):
    """Configuration for a specific failure scenario simulation."""

    scenario: FailureScenario
    trigger_after_seconds: int = Field(
        ..., ge=0, description="When to start the failure (seconds into simulation)"
    )
    progression_rate: float = Field(
        ..., ge=0, le=1, description="How fast failure progresses (0.0-1.0)"
    )
    baseline_probability: float = Field(
        ..., ge=0, le=1, description="Starting failure probability"
    )
    affected_metrics: list[str] = Field(
        ..., description="Telemetry metrics affected by this scenario"
    )
    noise_level: float = Field(
        default=0.1, ge=0, le=1, description="Random variation level"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "scenario": "engine_overheat",
                "trigger_after_seconds": 300,
                "progression_rate": 0.5,
                "baseline_probability": 0.2,
                "affected_metrics": [
                    "engine_temp_celsius",
                    "coolant_temp_celsius",
                    "engine_rpm",
                ],
                "noise_level": 0.15,
            }
        }
    }


class SimulationConfig(BaseModel):
    """Configuration for entire simulation run."""

    simulation_id: str = Field(..., description="Unique simulation identifier")
    duration_seconds: int = Field(
        default=3600, ge=0, description="Total simulation duration"
    )
    num_vehicles: int = Field(
        default=10, ge=1, description="Number of vehicles to simulate"
    )
    vehicle_types: dict[VehicleType, int] = Field(
        default_factory=lambda: {
            VehicleType.AMBULANCE: 6,
            VehicleType.FIRE_TRUCK: 4,
        },
        description="Distribution of vehicle types",
    )

    # Failure injection
    inject_failures: bool = Field(
        default=True, description="Whether to inject failures"
    )
    failure_scenarios: list[FailureScenario] = Field(
        default_factory=list, description="Specific scenarios to simulate"
    )
    random_failure_probability: float = Field(
        default=0.05, ge=0, le=1, description="Random failure probability per vehicle"
    )

    # Telemetry generation
    telemetry_frequency_hz: float = Field(
        default=1.0, ge=0.1, le=10.0, description="Telemetry generation frequency"
    )
    add_realistic_noise: bool = Field(
        default=True, description="Add realistic sensor noise"
    )
    simulate_gps_drift: bool = Field(
        default=True, description="Simulate GPS inaccuracy"
    )

    # Operational patterns
    dispatch_probability_per_hour: float = Field(
        default=2.0, ge=0, description="Average dispatches per hour"
    )
    mission_duration_avg_minutes: int = Field(
        default=30, ge=1, description="Average mission duration"
    )

    # Environmental simulation
    weather_conditions: str = Field(
        default="clear",
        description="Weather type (clear, rain, snow, extreme_heat)",
    )
    time_of_day: str = Field(default="day", description="Time of day (day, night)")

    model_config = {
        "json_schema_extra": {
            "example": {
                "simulation_id": "sim-2026-02-10-001",
                "duration_seconds": 3600,
                "num_vehicles": 10,
                "vehicle_types": {"ambulance": 6, "fire_truck": 4},
                "inject_failures": True,
                "failure_scenarios": [
                    "engine_overheat",
                    "alternator_failure",
                    "battery_degradation",
                ],
                "random_failure_probability": 0.05,
                "telemetry_frequency_hz": 1.0,
                "weather_conditions": "clear",
            }
        }
    }


class WeatherConditions(BaseModel):
    """Environmental conditions affecting vehicle performance."""

    condition_type: str = Field(
        ..., description="Weather type (clear, rain, snow, extreme_heat)"
    )
    ambient_temp_celsius: float = Field(..., description="Ambient temperature")
    humidity_percent: float = Field(
        ..., ge=0, le=100, description="Humidity percentage"
    )
    road_friction: float = Field(
        default=1.0, ge=0, le=1.0, description="Road friction coefficient"
    )
    visibility_factor: float = Field(
        default=1.0, ge=0, le=1.0, description="Visibility factor (1.0 = clear)"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "condition_type": "clear",
                    "ambient_temp_celsius": 20.0,
                    "humidity_percent": 50.0,
                    "road_friction": 1.0,
                    "visibility_factor": 1.0,
                },
                {
                    "condition_type": "rain",
                    "ambient_temp_celsius": 15.0,
                    "humidity_percent": 85.0,
                    "road_friction": 0.7,
                    "visibility_factor": 0.6,
                },
                {
                    "condition_type": "extreme_heat",
                    "ambient_temp_celsius": 40.0,
                    "humidity_percent": 30.0,
                    "road_friction": 0.95,
                    "visibility_factor": 0.9,
                },
            ]
        }
    }
