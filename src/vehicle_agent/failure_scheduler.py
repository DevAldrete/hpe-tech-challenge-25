"""
Automatic failure scheduling system using a Poisson process.
"""

import math
import random
from collections.abc import Callable

import structlog

from src.models.enums import FailureScenario

logger = structlog.get_logger(__name__)


class FailureScheduler:
    """Schedules automatic failure injection using a Poisson process."""

    def __init__(self, failure_rate_per_hour: float = 1.0) -> None:
        """
        Initialize the scheduler.

        Args:
            failure_rate_per_hour: Average number of failures per hour (lambda).
                                   Set to 1.0 to get a reasonable amount of simulated failures.
        """
        self.failure_rate_per_hour = failure_rate_per_hour

    def tick(self, dt_hours: float, activate_callback: Callable[[FailureScenario], None]) -> None:
        """
        Evaluate if a failure should occur in this time step.

        Args:
            dt_hours: Time step in hours.
            activate_callback: Callback function to trigger the failure.
        """
        if self.failure_rate_per_hour <= 0:
            return

        # Poisson probability of at least one event in dt_hours:
        # P(X >= 1) = 1 - P(X = 0) = 1 - exp(-lambda * dt)
        prob = 1.0 - math.exp(-self.failure_rate_per_hour * dt_hours)

        if random.random() < prob:
            scenario = random.choice(list(FailureScenario))
            logger.info("scheduling_failure", scenario=scenario.value)
            activate_callback(scenario)
