"""
Script to generate synthetic telemetry data and train a ML model for anomaly detection.
"""

import os

import joblib
import pandas as pd
import structlog
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from src.ml.feature_extractor import FeatureExtractor
from src.models.enums import FailureScenario, OperationalStatus, VehicleType
from src.vehicle_agent.config import AgentConfig
from src.vehicle_agent.failure_injector import FailureInjector
from src.vehicle_agent.telemetry_generator import SimpleTelemetryGenerator

logger = structlog.get_logger(__name__)


def generate_synthetic_data(num_samples: int = 10000) -> pd.DataFrame:
    """Generate synthetic telemetry data with and without failures."""

    config = AgentConfig(
        vehicle_id="TRN-001",
        vehicle_type=VehicleType.AMBULANCE,
        telemetry_frequency_hz=1.0,
    )
    generator = SimpleTelemetryGenerator(config)
    injector = FailureInjector()

    # We will run 3 scenarios: NORMAL, ENGINE_OVERHEAT, BATTERY_DEGRADATION, FUEL_LEAK
    # Each scenario gets equal number of ticks.

    data = []

    scenarios_to_run = [
        None,  # Normal
        FailureScenario.ENGINE_OVERHEAT,
        FailureScenario.BATTERY_DEGRADATION,
        FailureScenario.FUEL_LEAK,
    ]

    samples_per_scenario = num_samples // len(scenarios_to_run)

    for scenario in scenarios_to_run:
        extractor = FeatureExtractor(window_size=10)

        # Reset injector
        injector.active_scenarios.clear()
        if scenario:
            injector.activate_scenario(scenario)

        for _ in range(samples_per_scenario):
            # Generate raw telemetry
            telemetry = generator.generate(OperationalStatus.EN_ROUTE)

            # Apply failure
            telemetry = injector.apply_failures(telemetry)

            # Extract features
            extractor.add_telemetry(telemetry)
            features = extractor.extract_features()

            if features:
                features["label"] = scenario.value if scenario else "normal"
                data.append(features)

    return pd.DataFrame(data)


def train_model(output_path: str = "src/ml/model.joblib") -> None:
    """Train the RandomForestClassifier and save it."""
    logger.info("generating_synthetic_data")
    df = generate_synthetic_data(num_samples=10000)

    logger.info("training_model", samples=len(df))

    X = df.drop(columns=["label"])
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=50, max_depth=10, random_state=42)
    clf.fit(X_train, y_train)

    # Evaluate
    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred)
    logger.info("model_evaluation", report=f"\n{report}")

    # Ensure directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save model
    joblib.dump(clf, output_path)
    logger.info("model_saved", path=output_path)


if __name__ == "__main__":
    train_model()
