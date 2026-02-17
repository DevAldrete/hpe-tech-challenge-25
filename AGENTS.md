# Agent Development Guide - Project AEGIS

**Project:** HPE GreenLake Tech Challenge - Digital Twin Emergency Vehicle System  
**Language:** Python 3.13  
**Package Manager:** uv  
**Status:** POC Development Phase

---

## 🛠️ Development Commands

### Environment & Running
```bash
# Install dependencies
uv sync                           # All dependencies (including dev)
uv sync --no-dev                  # Production only

# Run application
uv run python main.py             # Main entry point
uv run aegis-vehicle              # Vehicle simulation
uv run aegis-orchestrator         # Central coordinator
uv run aegis-fleet                # Fleet simulation
```

### Testing
```bash
# Basic test commands
uv run pytest                                              # All tests with coverage
uv run pytest tests/unit/models/test_vehicle.py           # Specific file
uv run pytest tests/unit/models/test_vehicle.py::TestGeoLocation  # Specific class
uv run pytest tests/unit/models/test_vehicle.py::TestGeoLocation::test_geolocation_valid_creation  # Single test

# Advanced options
uv run pytest -m unit                       # Only unit tests
uv run pytest -m integration                # Only integration tests
uv run pytest -m "not slow"                 # Exclude slow tests
uv run pytest -n auto                       # Parallel execution
uv run pytest --cov-report=html             # HTML coverage report (htmlcov/)
uv run pytest --cov=src --cov-report=term-missing  # Show missing coverage
```

### Linting & Formatting
```bash
uv run ruff format .              # Format code (auto-fix)
uv run ruff check .               # Run linter
uv run ruff check --fix .         # Fix auto-fixable issues
uv run mypy src/                  # Type checking (strict mode)
uv run bandit -r src/             # Security scanning
uv run pydocstyle src/            # Docstring validation (Google style)
pre-commit run --all-files        # Run all pre-commit hooks
```

---

## 📁 Project Structure

```
src/
├── vehicle_agent/     # Vehicle digital twin agents
├── orchestrator/      # Central brain/coordinator
├── models/            # Pydantic data models (validation & serialization)
├── ml/                # Machine learning models
├── storage/           # Database & persistence
├── dashboard/         # Web dashboard
├── scripts/           # CLI entry points (aegis-* commands)
└── utils/             # Shared utilities

tests/
├── unit/              # Fast unit tests
├── integration/       # Integration tests
├── fixtures/          # Shared pytest fixtures
└── conftest.py        # Pytest configuration
```

---

## 🎨 Code Style Guidelines

### Import Order (PEP 8)
```python
# 1. Standard library
import os
from typing import Optional, Dict

# 2. Third-party
import numpy as np
from pydantic import BaseModel

# 3. Local application
from src.models.vehicle import VehicleIdentity
from src.utils.telemetry import generate_telemetry
```

### Type Hints (Required)
```python
def calculate_failure_probability(
    telemetry_data: Dict[str, float],
    threshold: float = 0.85
) -> tuple[bool, float]:
    """Calculate predictive failure probability.
    
    Args:
        telemetry_data: Sensor readings from vehicle
        threshold: Decision threshold for alerts
        
    Returns:
        Tuple of (is_critical, probability_score)
        
    Raises:
        ValueError: If telemetry_data is empty
    """
    pass
```

### Naming Conventions
- **Classes:** `PascalCase` → `VehicleDigitalTwin`, `TelemetryProcessor`
- **Functions/Methods:** `snake_case` → `process_telemetry`, `send_alert`
- **Constants:** `UPPER_SNAKE_CASE` → `MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT`
- **Private:** `_leading_underscore` → `_validate_data`, `_internal_helper`
- **Modules:** `lowercase` or `snake_case` → `vehicle.py`, `telemetry.py`

### Docstrings (Google Style - Required)
```python
class VehicleDigitalTwin:
    """Digital twin representation of an emergency vehicle.
    
    Simulates vehicle behavior, generates telemetry, and performs
    predictive maintenance calculations.
    
    Attributes:
        vehicle_id: Unique identifier (e.g., AMB-001)
        vehicle_type: VehicleType enum (ambulance, fire_truck, etc.)
        telemetry_interval: Seconds between telemetry updates
    """
```

### Error Handling (Explicit)
```python
# ✅ Good: Specific exceptions
try:
    telemetry = await fetch_vehicle_data(vehicle_id)
except ConnectionError as e:
    logger.error(f"Connection failed for {vehicle_id}: {e}")
    raise
except TimeoutError:
    logger.warning(f"Timeout for {vehicle_id}")
    return None

# ❌ Bad: Bare except
try:
    risky_operation()
except:  # Never do this
    pass
```

### Async/Await (I/O Operations)
```python
async def process_vehicle_fleet(vehicle_ids: list[str]) -> dict[str, Any]:
    """Process telemetry for entire fleet concurrently."""
    tasks = [fetch_and_analyze(vid) for vid in vehicle_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {vid: result for vid, result in zip(vehicle_ids, results)}
```

---

## 🏛️ Architecture Patterns

### Vehicle Agent Pattern
Each vehicle agent:
1. Generates synthetic telemetry (speed, temp, vibration, etc.)
2. Runs local anomaly detection (autonomous)
3. Publishes via Redis/MQTT message broker
4. Operates independently if central brain disconnects

### Message Broker Communication
```python
# Publish telemetry
await redis_client.publish(
    f"vehicle:{vehicle_id}:telemetry",
    json.dumps(telemetry_data)
)

# Subscribe to alerts
async for message in pubsub.listen():
    if message["type"] == "message":
        await handle_alert(message["data"])
```

---

## ✅ Testing Standards

### Test Organization
- **File naming:** `test_<module_name>.py` (mirrors source structure)
- **Class naming:** `TestClassName` → `TestGeoLocation`, `TestVehicleTelemetry`
- **Function naming:** `test_<what>_<condition>_<expected>` → `test_geolocation_latitude_bounds`

### Pytest Markers
```python
@pytest.mark.unit          # Fast unit tests
@pytest.mark.integration   # Integration tests
@pytest.mark.slow          # Long-running tests
@pytest.mark.simulation    # Simulation tests
```

### Fixtures & Mocking
```python
@pytest.fixture
def sample_telemetry() -> dict:
    """Sample telemetry for testing."""
    return {
        "vehicle_id": "AMB-001",
        "speed": 65.0,
        "engine_temp": 95.5,
        "timestamp": "2026-02-10T12:00:00Z"
    }

@pytest.mark.asyncio
async def test_redis_publish(sample_telemetry: dict) -> None:
    """Test telemetry publishing to Redis."""
    with patch('redis.asyncio.Redis.publish', new_callable=AsyncMock) as mock:
        await publish_telemetry(sample_telemetry)
        mock.assert_called_once()
```

---

## 📊 Configuration Summary

**pyproject.toml:**
- Line length: 100 chars
- Python: 3.13 (strict)
- Type checking: mypy strict mode
- Docstrings: Google convention
- Coverage reports: `htmlcov/`

**Pre-commit hooks:**
- Ruff linting & formatting
- MyPy type checking (src/ only)
- Bandit security scanning
- Pydocstyle validation
- File hygiene (whitespace, EOF)

---

## 🔒 Security & Best Practices

1. **Never commit secrets** → Use `.env` files (excluded from git)
2. **Validate all inputs** → Use Pydantic models for data validation
3. **Type everything** → mypy strict mode enforced
4. **Structured logging** → Use `structlog` for JSON logs
5. **Timeout all I/O** → Network calls must have timeouts
6. **Context managers** → Always use `with` or `async with` for resources

---

## 🌿 Git Workflow

- `main` → Stable, tested code (POC ready)
- `release` → Integration branch for new features
- `feature/*` → Feature branches (e.g., `feature/simulacion-motor`)

**Before committing:** Ensure tests pass and code is linted.

---

## 📚 Resources

- **README:** Project overview and vision
- **TESTING.md:** Detailed testing guidelines
- **docs/:** Architecture documentation (DATA_ARCHITECTURE.md, SIMULATION.md, etc.)
- **Python Version:** 3.13 (see `.python-version`)
- **License:** GNU GPL v3.0
