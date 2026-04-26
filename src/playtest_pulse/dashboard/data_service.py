from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from playtest_pulse.analytics import (
    calculate_average_damage_taken_by_level,
    calculate_deaths_by_level,
    calculate_enemy_defeats,
    calculate_item_pickups,
    get_most_picked_up_item,
    summarize_combat,
    summarize_level_performance,
    summarize_sessions,
)
from playtest_pulse.config import AppConfig
from playtest_pulse.storage import TelemetryRepository


# ---------------------------------------------------------------------------
# DashboardData
#
# Stores the prepared data needed by the Streamlit dashboard.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DashboardData:
    raw_events: pd.DataFrame
    session_summary: dict[str, int | float]
    level_performance: pd.DataFrame
    deaths_by_level: pd.DataFrame
    enemy_defeats: pd.DataFrame
    average_damage_by_level: pd.DataFrame
    item_pickups: pd.DataFrame
    combat_summary: dict[str, int]
    most_picked_up_item: str | None


# ---------------------------------------------------------------------------
# load_dashboard_data
#
# Loads telemetry events from SQLite storage and prepares dashboard metrics.
# ---------------------------------------------------------------------------
def load_dashboard_data(config: AppConfig) -> DashboardData:
    database_path = Path(config.data.processed_database_path)

    if not database_path.is_file():
        raise FileNotFoundError(
            f"Telemetry database does not exist: {database_path}. "
            "Generate sample data and run storage ingestion before opening the dashboard."
        )

    repository = TelemetryRepository(database_path)

    try:
        event_frame = repository.fetch_events_frame()
    finally:
        repository.close()

    if event_frame.empty:
        raise ValueError("Telemetry database does not contain any events.")

    return DashboardData(
        raw_events=event_frame,
        session_summary=summarize_sessions(event_frame),
        level_performance=summarize_level_performance(event_frame),
        deaths_by_level=calculate_deaths_by_level(event_frame),
        enemy_defeats=calculate_enemy_defeats(event_frame),
        average_damage_by_level=calculate_average_damage_taken_by_level(
            event_frame,
        ),
        item_pickups=calculate_item_pickups(event_frame),
        combat_summary=summarize_combat(event_frame),
        most_picked_up_item=get_most_picked_up_item(event_frame),
    )
