"""
Unit tests for alerts.py models.

Tests cover PredictiveAlert and MaintenanceRecommendation models.
"""

from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from src.models.alerts import MaintenanceRecommendation, PredictiveAlert
from src.models.enums import (
    AlertSeverity,
    FailureCategory,
    MaintenanceUrgency,
)


@pytest.mark.unit
@pytest.mark.models
class TestPredictiveAlert:
    """Test PredictiveAlert model validation and behavior."""

    def test_predictive_alert_valid_creation(self, sample_predictive_alert_data: dict) -> None:
        """Test creating a valid PredictiveAlert instance."""
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.vehicle_id == "AMB-001"
        assert alert.severity == AlertSeverity.WARNING
        assert alert.category == FailureCategory.ELECTRICAL
        assert alert.component == "alternator"
        assert alert.failure_probability == 0.75
        assert alert.confidence == 0.88
        assert alert.predicted_failure_likely_hours == 12.0
        assert alert.can_complete_current_mission is True
        assert alert.safe_to_operate is True

    def test_predictive_alert_auto_generates_id(self, sample_predictive_alert_data: dict) -> None:
        """Test alert_id is auto-generated if not provided."""
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.alert_id is not None
        assert isinstance(alert.alert_id, str)
        assert len(alert.alert_id) > 0

    def test_predictive_alert_failure_probability_bounds(
        self, sample_predictive_alert_data: dict
    ) -> None:
        """Test failure_probability must be between 0.0 and 1.0."""
        sample_predictive_alert_data["failure_probability"] = 1.5
        with pytest.raises(ValidationError):
            PredictiveAlert(**sample_predictive_alert_data)

        sample_predictive_alert_data["failure_probability"] = -0.1
        with pytest.raises(ValidationError):
            PredictiveAlert(**sample_predictive_alert_data)

        # Test boundaries
        sample_predictive_alert_data["failure_probability"] = 0.0
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.failure_probability == 0.0

        sample_predictive_alert_data["failure_probability"] = 1.0
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.failure_probability == 1.0

    def test_predictive_alert_confidence_bounds(self, sample_predictive_alert_data: dict) -> None:
        """Test confidence must be between 0.0 and 1.0."""
        sample_predictive_alert_data["confidence"] = 1.5
        with pytest.raises(ValidationError):
            PredictiveAlert(**sample_predictive_alert_data)

        sample_predictive_alert_data["confidence"] = -0.1
        with pytest.raises(ValidationError):
            PredictiveAlert(**sample_predictive_alert_data)

    def test_predictive_alert_time_window_non_negative(
        self, sample_predictive_alert_data: dict
    ) -> None:
        """Test predicted failure hours must be non-negative."""
        sample_predictive_alert_data["predicted_failure_min_hours"] = -1.0
        with pytest.raises(ValidationError):
            PredictiveAlert(**sample_predictive_alert_data)

        sample_predictive_alert_data["predicted_failure_min_hours"] = 0.0
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.predicted_failure_min_hours == 0.0

    def test_predictive_alert_severity_enum(self, sample_predictive_alert_data: dict) -> None:
        """Test severity must be valid AlertSeverity enum."""
        for severity in AlertSeverity:
            sample_predictive_alert_data["severity"] = severity
            alert = PredictiveAlert(**sample_predictive_alert_data)
            assert alert.severity == severity

    def test_predictive_alert_category_enum(self, sample_predictive_alert_data: dict) -> None:
        """Test category must be valid FailureCategory enum."""
        sample_predictive_alert_data["category"] = FailureCategory.ENGINE
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.category == FailureCategory.ENGINE

    def test_predictive_alert_contributing_factors_default(
        self, sample_predictive_alert_data: dict
    ) -> None:
        """Test contributing_factors defaults to empty list."""
        del sample_predictive_alert_data["contributing_factors"]
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.contributing_factors == []

    def test_predictive_alert_related_telemetry_default(
        self, sample_predictive_alert_data: dict
    ) -> None:
        """Test related_telemetry defaults to empty dict."""
        del sample_predictive_alert_data["related_telemetry"]
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.related_telemetry == {}

    def test_predictive_alert_acknowledgment_defaults(
        self, sample_predictive_alert_data: dict
    ) -> None:
        """Test acknowledgment fields default to False/None."""
        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.acknowledged is False
        assert alert.acknowledged_by is None
        assert alert.acknowledged_at is None

    def test_predictive_alert_can_be_acknowledged(self, sample_predictive_alert_data: dict) -> None:
        """Test alert can be updated with acknowledgment info."""
        sample_predictive_alert_data["acknowledged"] = True
        sample_predictive_alert_data["acknowledged_by"] = "dispatcher_001"
        sample_predictive_alert_data["acknowledged_at"] = datetime.now(timezone.utc)

        alert = PredictiveAlert(**sample_predictive_alert_data)
        assert alert.acknowledged is True
        assert alert.acknowledged_by == "dispatcher_001"
        assert alert.acknowledged_at is not None

    def test_predictive_alert_serialization(self, sample_predictive_alert_data: dict) -> None:
        """Test JSON serialization and deserialization."""
        alert = PredictiveAlert(**sample_predictive_alert_data)
        json_data = alert.model_dump()

        assert json_data["vehicle_id"] == "AMB-001"
        assert json_data["severity"] == "warning"
        assert json_data["component"] == "alternator"

        # Test round-trip
        alert_from_json = PredictiveAlert(**json_data)
        assert alert_from_json.vehicle_id == alert.vehicle_id
        assert alert_from_json.failure_probability == alert.failure_probability


@pytest.mark.unit
@pytest.mark.models
class TestMaintenanceRecommendation:
    """Test MaintenanceRecommendation model validation and behavior."""

    def test_maintenance_recommendation_valid_creation(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test creating a valid MaintenanceRecommendation instance."""
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.vehicle_id == "AMB-001"
        assert rec.urgency == MaintenanceUrgency.URGENT
        assert rec.component == "alternator"
        assert rec.issue_description == "Alternator output voltage declining, bearing wear detected"
        assert rec.recommended_action == "Replace alternator assembly"
        assert rec.estimated_downtime_hours == 2.5
        assert rec.estimated_labor_hours == 2.0
        assert rec.estimated_cost_usd == 450.00

    def test_maintenance_recommendation_auto_generates_id(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test recommendation_id is auto-generated if not provided."""
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.recommendation_id is not None
        assert isinstance(rec.recommendation_id, str)
        assert len(rec.recommendation_id) > 0

    def test_maintenance_recommendation_urgency_enum(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test urgency must be valid MaintenanceUrgency enum."""
        for urgency in MaintenanceUrgency:
            sample_maintenance_recommendation_data["urgency"] = urgency
            rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
            assert rec.urgency == urgency

    def test_maintenance_recommendation_downtime_non_negative(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test estimated_downtime_hours must be non-negative."""
        sample_maintenance_recommendation_data["estimated_downtime_hours"] = -1.0
        with pytest.raises(ValidationError):
            MaintenanceRecommendation(**sample_maintenance_recommendation_data)

        sample_maintenance_recommendation_data["estimated_downtime_hours"] = 0.0
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.estimated_downtime_hours == 0.0

    def test_maintenance_recommendation_labor_hours_non_negative(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test estimated_labor_hours must be non-negative."""
        sample_maintenance_recommendation_data["estimated_labor_hours"] = -1.0
        with pytest.raises(ValidationError):
            MaintenanceRecommendation(**sample_maintenance_recommendation_data)

    def test_maintenance_recommendation_cost_non_negative(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test estimated_cost_usd must be non-negative when provided."""
        sample_maintenance_recommendation_data["estimated_cost_usd"] = -100.0
        with pytest.raises(ValidationError):
            MaintenanceRecommendation(**sample_maintenance_recommendation_data)

        sample_maintenance_recommendation_data["estimated_cost_usd"] = 0.0
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.estimated_cost_usd == 0.0

    def test_maintenance_recommendation_cost_optional(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test estimated_cost_usd is optional."""
        sample_maintenance_recommendation_data["estimated_cost_usd"] = None
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.estimated_cost_usd is None

    def test_maintenance_recommendation_parts_needed_default(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test parts_needed defaults to empty list."""
        del sample_maintenance_recommendation_data["parts_needed"]
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.parts_needed == []

    def test_maintenance_recommendation_deferral_info_optional(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test deferral_risk is optional."""
        sample_maintenance_recommendation_data["deferral_risk"] = None
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        assert rec.deferral_risk is None

    def test_maintenance_recommendation_serialization(
        self, sample_maintenance_recommendation_data: dict
    ) -> None:
        """Test JSON serialization and deserialization."""
        rec = MaintenanceRecommendation(**sample_maintenance_recommendation_data)
        json_data = rec.model_dump()

        assert json_data["vehicle_id"] == "AMB-001"
        assert json_data["urgency"] == "urgent"
        assert json_data["component"] == "alternator"

        # Test round-trip
        rec_from_json = MaintenanceRecommendation(**json_data)
        assert rec_from_json.vehicle_id == rec.vehicle_id
        assert rec_from_json.estimated_cost_usd == rec.estimated_cost_usd
