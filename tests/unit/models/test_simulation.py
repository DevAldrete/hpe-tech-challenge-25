"""
Unit tests for simulation.py models.

Tests cover ScenarioParameters, SimulationConfig, and WeatherConditions models.
"""

import pytest
from pydantic import ValidationError

from src.models.enums import FailureScenario, VehicleType
from src.models.simulation import ScenarioParameters, SimulationConfig, WeatherConditions


@pytest.mark.unit
@pytest.mark.models
class TestScenarioParameters:
    """Test ScenarioParameters model validation and behavior."""

    def test_scenario_parameters_valid_creation(
        self, sample_scenario_parameters_data: dict
    ) -> None:
        """Test creating a valid ScenarioParameters instance."""
        params = ScenarioParameters(**sample_scenario_parameters_data)
        assert params.scenario == FailureScenario.ENGINE_OVERHEAT
        assert params.trigger_after_seconds == 300
        assert params.progression_rate == 0.5
        assert params.baseline_probability == 0.2
        assert len(params.affected_metrics) == 3
        assert params.noise_level == 0.15

    def test_scenario_parameters_scenario_enum(self, sample_scenario_parameters_data: dict) -> None:
        """Test scenario must be valid FailureScenario enum."""
        sample_scenario_parameters_data["scenario"] = FailureScenario.ALTERNATOR_FAILURE
        params = ScenarioParameters(**sample_scenario_parameters_data)
        assert params.scenario == FailureScenario.ALTERNATOR_FAILURE

    def test_scenario_parameters_trigger_non_negative(
        self, sample_scenario_parameters_data: dict
    ) -> None:
        """Test trigger_after_seconds must be non-negative."""
        sample_scenario_parameters_data["trigger_after_seconds"] = -1
        with pytest.raises(ValidationError):
            ScenarioParameters(**sample_scenario_parameters_data)

        sample_scenario_parameters_data["trigger_after_seconds"] = 0
        params = ScenarioParameters(**sample_scenario_parameters_data)
        assert params.trigger_after_seconds == 0

    def test_scenario_parameters_progression_rate_bounds(
        self, sample_scenario_parameters_data: dict
    ) -> None:
        """Test progression_rate must be between 0.0 and 1.0."""
        sample_scenario_parameters_data["progression_rate"] = 1.5
        with pytest.raises(ValidationError):
            ScenarioParameters(**sample_scenario_parameters_data)

        sample_scenario_parameters_data["progression_rate"] = -0.1
        with pytest.raises(ValidationError):
            ScenarioParameters(**sample_scenario_parameters_data)

    def test_scenario_parameters_baseline_probability_bounds(
        self, sample_scenario_parameters_data: dict
    ) -> None:
        """Test baseline_probability must be between 0.0 and 1.0."""
        sample_scenario_parameters_data["baseline_probability"] = 1.1
        with pytest.raises(ValidationError):
            ScenarioParameters(**sample_scenario_parameters_data)

    def test_scenario_parameters_noise_level_bounds(
        self, sample_scenario_parameters_data: dict
    ) -> None:
        """Test noise_level must be between 0.0 and 1.0."""
        sample_scenario_parameters_data["noise_level"] = 1.5
        with pytest.raises(ValidationError):
            ScenarioParameters(**sample_scenario_parameters_data)

    def test_scenario_parameters_noise_level_default(
        self, sample_scenario_parameters_data: dict
    ) -> None:
        """Test noise_level defaults to 0.1."""
        del sample_scenario_parameters_data["noise_level"]
        params = ScenarioParameters(**sample_scenario_parameters_data)
        assert params.noise_level == 0.1

    def test_scenario_parameters_serialization(self, sample_scenario_parameters_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        params = ScenarioParameters(**sample_scenario_parameters_data)
        json_data = params.model_dump()

        assert json_data["scenario"] == "engine_overheat"
        assert json_data["trigger_after_seconds"] == 300

        # Test round-trip
        params_from_json = ScenarioParameters(**json_data)
        assert params_from_json.scenario == params.scenario


@pytest.mark.unit
@pytest.mark.models
class TestSimulationConfig:
    """Test SimulationConfig model validation and behavior."""

    def test_simulation_config_valid_creation(self, sample_simulation_config_data: dict) -> None:
        """Test creating a valid SimulationConfig instance."""
        config = SimulationConfig(**sample_simulation_config_data)
        assert config.simulation_id == "sim-2026-02-10-001"
        assert config.duration_seconds == 3600
        assert config.num_vehicles == 10
        assert config.vehicle_types[VehicleType.AMBULANCE] == 6
        assert config.vehicle_types[VehicleType.FIRE_TRUCK] == 4
        assert config.inject_failures is True

    def test_simulation_config_duration_non_negative(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test duration_seconds must be non-negative."""
        sample_simulation_config_data["duration_seconds"] = -1
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

    def test_simulation_config_num_vehicles_positive(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test num_vehicles must be at least 1."""
        sample_simulation_config_data["num_vehicles"] = 0
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

        sample_simulation_config_data["num_vehicles"] = 1
        config = SimulationConfig(**sample_simulation_config_data)
        assert config.num_vehicles == 1

    def test_simulation_config_vehicle_types_default(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test vehicle_types has default distribution."""
        del sample_simulation_config_data["vehicle_types"]
        config = SimulationConfig(**sample_simulation_config_data)
        assert VehicleType.AMBULANCE in config.vehicle_types
        assert VehicleType.FIRE_TRUCK in config.vehicle_types

    def test_simulation_config_telemetry_frequency_bounds(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test telemetry_frequency_hz enforces 0.1 to 10.0 range."""
        sample_simulation_config_data["telemetry_frequency_hz"] = 0.05
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

        sample_simulation_config_data["telemetry_frequency_hz"] = 11.0
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

    def test_simulation_config_random_failure_probability_bounds(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test random_failure_probability must be between 0.0 and 1.0."""
        sample_simulation_config_data["random_failure_probability"] = 1.5
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

    def test_simulation_config_dispatch_probability_non_negative(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test dispatch_probability_per_hour must be non-negative."""
        sample_simulation_config_data["dispatch_probability_per_hour"] = -1.0
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

    def test_simulation_config_mission_duration_positive(
        self, sample_simulation_config_data: dict
    ) -> None:
        """Test mission_duration_avg_minutes must be at least 1."""
        sample_simulation_config_data["mission_duration_avg_minutes"] = 0
        with pytest.raises(ValidationError):
            SimulationConfig(**sample_simulation_config_data)

    def test_simulation_config_defaults(self) -> None:
        """Test default values for optional fields."""
        config = SimulationConfig(simulation_id="test-sim")
        assert config.duration_seconds == 3600
        assert config.num_vehicles == 10
        assert config.inject_failures is True
        assert config.telemetry_frequency_hz == 1.0
        assert config.add_realistic_noise is True
        assert config.weather_conditions == "clear"
        assert config.time_of_day == "day"

    def test_simulation_config_serialization(self, sample_simulation_config_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        config = SimulationConfig(**sample_simulation_config_data)
        json_data = config.model_dump()

        assert json_data["simulation_id"] == "sim-2026-02-10-001"
        assert json_data["num_vehicles"] == 10

        # Test round-trip
        config_from_json = SimulationConfig(**json_data)
        assert config_from_json.simulation_id == config.simulation_id
        assert config_from_json.num_vehicles == config.num_vehicles


@pytest.mark.unit
@pytest.mark.models
class TestWeatherConditions:
    """Test WeatherConditions model validation and behavior."""

    def test_weather_conditions_valid_creation(self, sample_weather_conditions_data: dict) -> None:
        """Test creating a valid WeatherConditions instance."""
        weather = WeatherConditions(**sample_weather_conditions_data)
        assert weather.condition_type == "clear"
        assert weather.ambient_temp_celsius == 20.0
        assert weather.humidity_percent == 50.0
        assert weather.road_friction == 1.0
        assert weather.visibility_factor == 1.0

    def test_weather_conditions_humidity_bounds(self, sample_weather_conditions_data: dict) -> None:
        """Test humidity_percent enforces 0 to 100 range."""
        sample_weather_conditions_data["humidity_percent"] = -1.0
        with pytest.raises(ValidationError):
            WeatherConditions(**sample_weather_conditions_data)

        sample_weather_conditions_data["humidity_percent"] = 101.0
        with pytest.raises(ValidationError):
            WeatherConditions(**sample_weather_conditions_data)

    def test_weather_conditions_road_friction_bounds(
        self, sample_weather_conditions_data: dict
    ) -> None:
        """Test road_friction enforces 0.0 to 1.0 range."""
        sample_weather_conditions_data["road_friction"] = 1.5
        with pytest.raises(ValidationError):
            WeatherConditions(**sample_weather_conditions_data)

        sample_weather_conditions_data["road_friction"] = -0.1
        with pytest.raises(ValidationError):
            WeatherConditions(**sample_weather_conditions_data)

    def test_weather_conditions_visibility_bounds(
        self, sample_weather_conditions_data: dict
    ) -> None:
        """Test visibility_factor enforces 0.0 to 1.0 range."""
        sample_weather_conditions_data["visibility_factor"] = 1.5
        with pytest.raises(ValidationError):
            WeatherConditions(**sample_weather_conditions_data)

    def test_weather_conditions_defaults(self, sample_weather_conditions_data: dict) -> None:
        """Test default values for optional fields."""
        del sample_weather_conditions_data["road_friction"]
        del sample_weather_conditions_data["visibility_factor"]
        weather = WeatherConditions(**sample_weather_conditions_data)
        assert weather.road_friction == 1.0
        assert weather.visibility_factor == 1.0

    def test_weather_conditions_serialization(self, sample_weather_conditions_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        weather = WeatherConditions(**sample_weather_conditions_data)
        json_data = weather.model_dump()

        assert json_data["condition_type"] == "clear"
        assert json_data["road_friction"] == 1.0

        # Test round-trip
        weather_from_json = WeatherConditions(**json_data)
        assert weather_from_json.condition_type == weather.condition_type
