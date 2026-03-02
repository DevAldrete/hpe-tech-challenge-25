"""
Machine Learning inference predictor for anomaly detection.
"""

import os
from datetime import UTC, datetime

import joblib
import pandas as pd
import structlog

from src.ml.feature_extractor import FeatureExtractor
from src.models.alerts import PredictiveAlert
from src.models.enums import AlertSeverity, FailureCategory, FailureScenario
from src.models.telemetry import VehicleTelemetry

logger = structlog.get_logger(__name__)


class Predictor:
    """Uses a trained RandomForest model to detect anomalies."""

    def __init__(self, vehicle_id: str, model_path: str = "src/ml/model.joblib") -> None:
        """
        Initialize the predictor.

        Args:
            vehicle_id: ID of the vehicle being monitored
            model_path: Path to the trained ML model
        """
        self.vehicle_id = vehicle_id
        self.extractor = FeatureExtractor(window_size=10)
        self.model = None

        if os.path.exists(model_path):
            try:
                self.model = joblib.load(model_path)
                logger.info("ml_model_loaded", vehicle_id=vehicle_id, path=model_path)
            except Exception as e:
                logger.error("ml_model_load_failed", error=str(e))
        else:
            logger.warning("ml_model_not_found", path=model_path, msg="Falling back to no-op")

    def analyze(self, telemetry: VehicleTelemetry) -> list[PredictiveAlert]:
        """
        Analyze telemetry using ML model.

        Args:
            telemetry: Current telemetry point

        Returns:
            List of generated predictive alerts
        """
        self.extractor.add_telemetry(telemetry)

        if self.model is None:
            return []

        features = self.extractor.extract_features()
        if not features:
            # Window not full yet
            return []

        # Predict
        df = pd.DataFrame([features])
        prediction = self.model.predict(df)[0]

        alerts = []

        # We assume labels match FailureScenario.value, plus 'normal'
        if prediction != "normal":
            severity = AlertSeverity.WARNING
            category = FailureCategory.OTHER
            safe_to_operate = True

            if prediction == FailureScenario.ENGINE_OVERHEAT.value:
                category = FailureCategory.ENGINE
                severity = AlertSeverity.CRITICAL
                safe_to_operate = False
                action = "STOP IMMEDIATELY - Critical engine overheat predicted."
            elif prediction == FailureScenario.BATTERY_DEGRADATION.value:
                category = FailureCategory.ELECTRICAL
                action = "Monitor electrical system. Impending battery failure."
            elif prediction == FailureScenario.FUEL_LEAK.value:
                category = FailureCategory.FUEL
                severity = AlertSeverity.CRITICAL
                action = "REFUEL IMMEDIATELY - Severe fuel leak detected."
            else:
                action = f"Anomaly detected: {prediction}"

            alert = PredictiveAlert(
                vehicle_id=self.vehicle_id,
                timestamp=datetime.now(UTC),
                severity=severity,
                category=category,
                component=prediction,
                failure_probability=0.85,  # Fake prob from simple ML
                confidence=0.90,
                predicted_failure_min_hours=0.5,
                predicted_failure_max_hours=2.0,
                predicted_failure_likely_hours=1.0,
                can_complete_current_mission=safe_to_operate,
                safe_to_operate=safe_to_operate,
                recommended_action=action,
                contributing_factors=["ML anomaly detection pattern matched"],
                related_telemetry=features,
            )
            alerts.append(alert)

        return alerts
