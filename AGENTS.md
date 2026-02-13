# Agent Development Guide - Project AEGIS

**Project:** HPE GreenLake Tech Challenge - Digital Twin Emergency Vehicle System  
**Language:** Python 3.13+  
**Package Manager:** uv  
**Status:** POC Development Phase

---

## 🛠️ Development Commands

### Environment Setup
```bash
# Install uv package manager (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Unix/macOS
# or
.venv\Scripts\activate  # Windows
```

### Running the Application
```bash
# Run main entry point
python main.py

# Run with uv
uv run main.py
```

### Testing
```bash
# Run all tests (when pytest is configured)
uv run pytest

# Run specific test file
uv run pytest tests/test_vehicle_node.py

# Run single test function
uv run pytest tests/test_vehicle_node.py::test_telemetry_generation

# Run with coverage
uv run pytest --cov=src --cov-report=html

# Run in verbose mode
uv run pytest -v

# Run with specific markers (when configured)
uv run pytest -m unit
uv run pytest -m integration
```

### Linting & Formatting
```bash
# Run ruff linter (when configured)
uv run ruff check .

# Fix auto-fixable issues
uv run ruff check --fix .

# Format code with ruff
uv run ruff format .

# Type checking with mypy (when configured)
uv run mypy src/
```

---

## 📁 Project Structure

```
hpe-tech-challenge-25/
├── src/                    # Source code root
│   ├── vehicle_nodes/     # Vehicle agent simulation logic
│   ├── orchestrator/      # Central brain/coordinator service
│   ├── telemetry/         # Telemetry generation and processing
│   ├── models/            # AI/ML models for predictive defense
│   └── utils/             # Shared utilities
├── tests/                 # Test suite
│   ├── unit/             # Unit tests
│   ├── integration/      # Integration tests
│   └── fixtures/         # Test fixtures and data
├── main.py               # Application entry point
├── pyproject.toml        # Project configuration
└── README.md             # Project documentation
```

---

## 🎨 Code Style Guidelines

### Import Order
Follow PEP 8 import ordering:
```python
# 1. Standard library imports
import os
import sys
from typing import Optional, List, Dict

# 2. Third-party imports
import numpy as np
import redis
from fastapi import FastAPI

# 3. Local application imports
from src.vehicle_nodes import VehicleAgent
from src.utils.telemetry import generate_telemetry
```

### Type Hints
Always use type hints for function signatures:
```python
def calculate_failure_probability(
    telemetry_data: Dict[str, float],
    model_threshold: float = 0.85
) -> tuple[bool, float]:
    """Calculate predictive failure probability.
    
    Args:
        telemetry_data: Sensor readings from vehicle
        model_threshold: Decision threshold for alerts
        
    Returns:
        Tuple of (is_critical, probability_score)
    """
    pass
```

### Naming Conventions
- **Classes:** `PascalCase` (e.g., `VehicleDigitalTwin`, `TelemetryProcessor`)
- **Functions/Methods:** `snake_case` (e.g., `process_telemetry`, `send_alert`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRY_ATTEMPTS`, `DEFAULT_TIMEOUT`)
- **Private methods:** `_leading_underscore` (e.g., `_validate_data`)
- **Module names:** `lowercase` or `snake_case` (e.g., `vehicle_nodes.py`, `telemetry.py`)

### Docstrings
Use Google-style docstrings:
```python
class VehicleDigitalTwin:
    """Digital twin representation of an emergency vehicle.
    
    This class simulates vehicle behavior, generates telemetry,
    and performs predictive maintenance calculations.
    
    Attributes:
        vehicle_id: Unique identifier for the vehicle
        vehicle_type: Type (ambulance, fire_truck, etc.)
        telemetry_interval: Seconds between telemetry updates
    """
    
    def predict_failure(self, component: str) -> float:
        """Predict failure probability for a vehicle component.
        
        Args:
            component: Component name (engine, transmission, etc.)
            
        Returns:
            Failure probability between 0.0 and 1.0
            
        Raises:
            ValueError: If component is not recognized
        """
        pass
```

### Error Handling
Be explicit with exception handling:
```python
# Good: Specific exception handling
try:
    telemetry = await fetch_vehicle_data(vehicle_id)
except ConnectionError as e:
    logger.error(f"Failed to connect to vehicle {vehicle_id}: {e}")
    raise
except TimeoutError:
    logger.warning(f"Timeout fetching data from {vehicle_id}")
    return None

# Avoid: Bare except clauses
try:
    risky_operation()
except:  # DON'T DO THIS
    pass
```

### Async/Await
Use async/await for I/O-bound operations:
```python
async def process_vehicle_fleet(vehicle_ids: List[str]) -> Dict[str, Any]:
    """Process telemetry for entire fleet concurrently."""
    tasks = [fetch_and_analyze(vid) for vid in vehicle_ids]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return {vid: result for vid, result in zip(vehicle_ids, results)}
```

---

## 🏛️ Architecture Guidelines

### Vehicle Node Pattern
Each vehicle agent should:
1. Generate synthetic telemetry (speed, temperature, vibration, etc.)
2. Run local anomaly detection
3. Communicate via message broker (Redis/MQTT)
4. Maintain autonomous operation if central brain disconnects

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

### Microservice Design
- Each service should have a single responsibility
- Use environment variables for configuration (never hardcode)
- Implement health check endpoints
- Include graceful shutdown handlers

---

## ✅ Testing Standards

### Test File Naming
- Test files: `test_<module_name>.py`
- Mirror source structure in `tests/` directory

### Test Function Naming
```python
def test_vehicle_generates_valid_telemetry():
    """Test that vehicle node produces correctly formatted data."""
    pass

def test_failure_prediction_above_threshold_triggers_alert():
    """Test alert triggering logic for high failure probability."""
    pass
```

### Fixtures and Mocking
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.fixture
def sample_telemetry():
    """Provide sample telemetry data for tests."""
    return {
        "vehicle_id": "AMB-001",
        "speed": 65.0,
        "engine_temp": 95.5,
        "timestamp": "2026-02-10T12:00:00Z"
    }

@pytest.mark.asyncio
async def test_redis_publish(sample_telemetry):
    """Test telemetry publishing to Redis."""
    with patch('redis.asyncio.Redis.publish', new_callable=AsyncMock) as mock_pub:
        await publish_telemetry(sample_telemetry)
        mock_pub.assert_called_once()
```

---

## 🔒 Security & Best Practices

1. **Never commit secrets** - Use environment variables or secret managers
2. **Validate all inputs** - Especially data from message brokers
3. **Use type checking** - Enable mypy strict mode when possible
4. **Log appropriately** - Use structured logging (e.g., structlog)
5. **Handle timeouts** - All I/O operations should have timeouts
6. **Resource cleanup** - Use context managers (`with` statements, `async with`)

---

## 🌿 Git Workflow

- `main` - Stable, tested code (POC ready)
- `release` - Integration branch for new features
- `feature/*` - Feature branches (e.g., `feature/simulacion-motor`)

Always ensure your code is tested and linted before committing.

---

## 📚 Additional Resources

- Project README: `README.md`
- Python Version: 3.13+ (see `.python-version`)
- License: GNU GPL v3.0
