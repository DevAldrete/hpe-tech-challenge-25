"""
Historical crime injector for simulation and model validation.

Synced with the AI simulation clock to inject crimes based on the
current simulated day of the week and hour.
"""

import asyncio
from pathlib import Path
import pandas as pd
from datetime import UTC, datetime, timedelta

import structlog

from src.models.emergency import (
    EMERGENCY_UNITS_DEFAULTS,
    Emergency,
    EmergencySeverity,
    EmergencyType,
    Location,
    scale_units_by_severity,
)
from src.orchestrator.agent import OrchestratorAgent

logger = structlog.get_logger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_CSV = PROJECT_ROOT / "data" / "delitos_sf.csv"

class HistoricalCrimeInjector:
    """Injects historical crimes into the orchestrator to test the AI."""

    def __init__(
        self,
        orchestrator: OrchestratorAgent,
        csv_path: str = str(DEFAULT_CSV),
        start_time: datetime | None = None,
        simulated_minutes_per_tick: int = 30,
        tick_interval_seconds: float = 3.0,
    ) -> None:
        """
        Initialize the historical injector.

        Args:
            orchestrator: The orchestrator to submit emergencies to.
            csv_path: Path to the dataset.
            start_time: The simulated start time (matches AI generator).
            simulated_minutes_per_tick: How many minutes to jump per tick.
            tick_interval_seconds: Real-time seconds between ticks.
        """
        self.orchestrator = orchestrator
        self.csv_path = csv_path
        self.current_sim_time = start_time or datetime.now()
        self.simulated_minutes_per_tick = simulated_minutes_per_tick
        self.tick_interval_seconds = tick_interval_seconds
        
        self.running = False
        self.holdout_data = pd.DataFrame()
        self.last_processed_time: tuple[int, int] | None = None

    def _prepare_data(self) -> None:
        """Load the CSV and extract the chronologically newest 20% of data."""
        try:
            df = pd.read_csv(self.csv_path)
            
            # Reconstruct datetime
            if 'fecha_dt' in df.columns:
                df['fecha_dt'] = pd.to_datetime(df['fecha_dt'], errors='coerce')
            elif 'fecha' in df.columns:
                df['fecha_dt'] = pd.to_datetime(df['fecha'], format='%d/%m/%Y', errors='coerce')
            
            # Ensure we have clean hour and day_of_week integers for matching
            if 'hour_int' not in df.columns:
                df['hour_int'] = pd.to_datetime(df['hora'], format='%H:%M', errors='coerce').dt.hour
            
            df['day_of_week'] = df['fecha_dt'].dt.dayofweek
            
            # Sort chronologically and take the last 20%
            df = df.sort_values(by=['fecha_dt', 'hora'])
            split_idx = int(len(df) * 0.8)
            self.holdout_data = df.iloc[split_idx:].copy()
            
            logger.info("historical_data_prepared", total_playback_events=len(self.holdout_data))
            
        except Exception as e:
            logger.error("failed_to_load_historical_data", error=str(e))

    async def start(self) -> None:
        """Start the playback loop synchronized with the simulated clock."""
        self._prepare_data()
        
        if self.holdout_data.empty:
            logger.error("no_data_to_playback")
            return

        self.running = True
        logger.info("historical_injector_started", start_sim_time=self.current_sim_time.isoformat())

        while self.running:
            current_dow = self.current_sim_time.weekday()
            current_hour = self.current_sim_time.hour

            # Only query and inject if the simulated hour has changed
            if (current_dow, current_hour) != self.last_processed_time:
                self.last_processed_time = (current_dow, current_hour)

                # Find crimes matching the current day of the week and hour
                matching_crimes = self.holdout_data[
                    (self.holdout_data['day_of_week'] == current_dow) &
                    (self.holdout_data['hour_int'] == current_hour)
                ]

                if not matching_crimes.empty:
                    # Pick 1 random crime from the matching pool so we don't flood the map
                    sampled_crimes = matching_crimes.sample(n=1)

                    for _, row in sampled_crimes.iterrows():
                        try:
                            await self._inject_crime(row)
                        except Exception as e:
                            logger.error("historical_injection_error", error=str(e), exc_info=True)

            # Advance the simulation clock
            self.current_sim_time += timedelta(minutes=self.simulated_minutes_per_tick)
            await asyncio.sleep(self.tick_interval_seconds)

    def stop(self) -> None:
        """Stop the playback loop."""
        self.running = False
        logger.info("historical_injector_stopped")

    async def _inject_crime(self, row: pd.Series) -> None:
        """Convert a historical CSV row into an AEGIS Emergency and dispatch it."""
        
        neighborhood = row.get('nombre_de_la_colonia', 'Unknown Area')
        crime_type_str = row.get('crime_type', 'crime').upper()
        
        severity = EmergencySeverity.HIGH 

        location = Location(
            latitude=float(row['latitud']), 
            longitude=float(row['longitud']), 
            timestamp=datetime.now(UTC)
        )

        em_type = EmergencyType.CRIME
        units_required = scale_units_by_severity(EMERGENCY_UNITS_DEFAULTS[em_type], severity)

        sim_time_str = self.current_sim_time.strftime('%A %H:%M')

        emergency = Emergency(
            emergency_type=em_type,
            severity=severity,
            location=location,
            address=neighborhood,
            description=f"ACTUAL CRIME [{sim_time_str}]: {crime_type_str} reported historically",
            units_required=units_required,
            reported_by="historical_playback",
        )

        logger.info("injecting_historical_crime", neighborhood=neighborhood, crime=crime_type_str, time=sim_time_str)

        await self.orchestrator.process_emergency(emergency)