from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from playtest_pulse.config import (
    AppConfig,
    DashboardConfig,
    DataConfig,
    GenerationConfig,
    ProjectConfig,
)
from playtest_pulse.dashboard import DashboardData, load_dashboard_data
from playtest_pulse.ingestion import generate_sample_events
from playtest_pulse.storage import TelemetryRepository


# ---------------------------------------------------------------------------
# _write_sample_database
#
# Writes generated sample telemetry events to a temporary SQLite database.
# ---------------------------------------------------------------------------
def _write_sample_database(tmp_path: Path) -> Path:
    events = generate_sample_events(
        project_config=ProjectConfig(
            name="playtest-pulse",
            version="0.1.0",
            seed=42,
        ),
        generation_config=GenerationConfig(
            player_count=5,
            min_sessions_per_player=1,
            max_sessions_per_player=2,
            level_count=3,
        ),
    )

    database_path = tmp_path / "telemetry.sqlite3"
    repository = TelemetryRepository(database_path)

    try:
        repository.insert_events(events)
    finally:
        repository.close()

    return database_path


# ---------------------------------------------------------------------------
# _app_config
#
# Builds a small app config that points to a temporary SQLite database.
# ---------------------------------------------------------------------------
def _app_config(database_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectConfig(
            name="playtest-pulse",
            version="0.1.0",
            seed=42,
        ),
        data=DataConfig(
            raw_events_path="unused.csv",
            processed_database_path=str(database_path),
        ),
        generation=GenerationConfig(
            player_count=5,
            min_sessions_per_player=1,
            max_sessions_per_player=2,
            level_count=3,
        ),
        dashboard=DashboardConfig(
            title="Playtest Pulse",
        ),
    )


# ---------------------------------------------------------------------------
# test_load_dashboard_data_returns_dashboard_data
#
# Verifies that dashboard data loading returns the expected data object.
# ---------------------------------------------------------------------------
def test_load_dashboard_data_returns_dashboard_data(tmp_path: Path) -> None:
    database_path = _write_sample_database(tmp_path)

    dashboard_data = load_dashboard_data(_app_config(database_path))

    assert isinstance(dashboard_data, DashboardData)


# ---------------------------------------------------------------------------
# test_load_dashboard_data_includes_raw_events_frame
#
# Verifies that loaded dashboard data includes a raw events DataFrame.
# ---------------------------------------------------------------------------
def test_load_dashboard_data_includes_raw_events_frame(tmp_path: Path) -> None:
    database_path = _write_sample_database(tmp_path)

    dashboard_data = load_dashboard_data(_app_config(database_path))

    assert isinstance(dashboard_data.raw_events, pd.DataFrame)
    assert not dashboard_data.raw_events.empty


# ---------------------------------------------------------------------------
# test_load_dashboard_data_includes_session_summary
#
# Verifies that dashboard data includes session-level summary metrics.
# ---------------------------------------------------------------------------
def test_load_dashboard_data_includes_session_summary(tmp_path: Path) -> None:
    database_path = _write_sample_database(tmp_path)

    dashboard_data = load_dashboard_data(_app_config(database_path))

    assert dashboard_data.session_summary["total_players"] == 5
    assert dashboard_data.session_summary["total_sessions"] >= 5
    assert dashboard_data.session_summary["average_session_duration_seconds"] > 0


# ---------------------------------------------------------------------------
# test_load_dashboard_data_includes_metric_tables
#
# Verifies that dashboard data includes the main metric tables.
# ---------------------------------------------------------------------------
def test_load_dashboard_data_includes_metric_tables(tmp_path: Path) -> None:
    database_path = _write_sample_database(tmp_path)

    dashboard_data = load_dashboard_data(_app_config(database_path))

    assert not dashboard_data.level_performance.empty
    assert isinstance(dashboard_data.deaths_by_level, pd.DataFrame)
    assert isinstance(dashboard_data.enemy_defeats, pd.DataFrame)
    assert isinstance(dashboard_data.average_damage_by_level, pd.DataFrame)
    assert isinstance(dashboard_data.item_pickups, pd.DataFrame)


# ---------------------------------------------------------------------------
# test_load_dashboard_data_includes_combat_and_item_summaries
#
# Verifies that dashboard data includes compact combat and item summaries.
# ---------------------------------------------------------------------------
def test_load_dashboard_data_includes_combat_and_item_summaries(
    tmp_path: Path,
) -> None:
    database_path = _write_sample_database(tmp_path)

    dashboard_data = load_dashboard_data(_app_config(database_path))

    assert "player_deaths" in dashboard_data.combat_summary
    assert "enemy_defeats" in dashboard_data.combat_summary
    assert dashboard_data.most_picked_up_item is None or isinstance(
        dashboard_data.most_picked_up_item,
        str,
    )


# ---------------------------------------------------------------------------
# test_load_dashboard_data_rejects_missing_database
#
# Verifies that dashboard loading fails clearly when the database is missing.
# ---------------------------------------------------------------------------
def test_load_dashboard_data_rejects_missing_database(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.sqlite3"

    with pytest.raises(FileNotFoundError, match="storage ingestion"):
        load_dashboard_data(_app_config(missing_path))
