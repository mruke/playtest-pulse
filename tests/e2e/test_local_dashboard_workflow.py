from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from playtest_pulse.config import (
    AppConfig,
    DashboardConfig,
    DataConfig,
    GenerationConfig,
    ProjectConfig,
)
from playtest_pulse.dashboard import DashboardData, load_dashboard_data
from playtest_pulse.ingestion import generate_sample_events, load_events_csv
from playtest_pulse.storage import TelemetryRepository


# ---------------------------------------------------------------------------
# _build_config
#
# Builds a small app config for the local end-to-end workflow test.
# ---------------------------------------------------------------------------
def _build_config(tmp_path: Path) -> AppConfig:
    return AppConfig(
        project=ProjectConfig(
            name="playtest-pulse-e2e",
            version="0.1.0-test",
            seed=123,
        ),
        data=DataConfig(
            raw_events_path=str(tmp_path / "sample_events.csv"),
            processed_database_path=str(tmp_path / "telemetry.sqlite3"),
        ),
        generation=GenerationConfig(
            player_count=4,
            min_sessions_per_player=1,
            max_sessions_per_player=2,
            level_count=3,
        ),
        dashboard=DashboardConfig(
            title="Playtest Pulse E2E",
        ),
    )


# ---------------------------------------------------------------------------
# _write_events_csv
#
# Writes generated telemetry events to CSV for the E2E workflow.
# ---------------------------------------------------------------------------
def _write_events_csv(config: AppConfig) -> None:
    events = generate_sample_events(
        project_config=config.project,
        generation_config=config.generation,
    )

    csv_path = Path(config.data.raw_events_path)
    fieldnames = [
        "event_id",
        "player_id",
        "session_id",
        "timestamp",
        "event_type",
        "level_id",
        "enemy_type",
        "item_id",
        "duration_seconds",
        "damage_taken",
        "result",
    ]

    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for event in events:
            writer.writerow(asdict(event))


# ---------------------------------------------------------------------------
# _ingest_events
#
# Loads generated CSV events and stores them in local SQLite storage.
# ---------------------------------------------------------------------------
def _ingest_events(config: AppConfig) -> None:
    events = load_events_csv(config.data.raw_events_path)
    repository = TelemetryRepository(config.data.processed_database_path)

    try:
        repository.insert_events(events)
    finally:
        repository.close()


# ---------------------------------------------------------------------------
# test_local_dashboard_workflow_end_to_end
#
# Verifies the local flow from generation to storage-backed dashboard data.
# ---------------------------------------------------------------------------
def test_local_dashboard_workflow_end_to_end(tmp_path: Path) -> None:
    config = _build_config(tmp_path)

    _write_events_csv(config)
    _ingest_events(config)

    dashboard_data = load_dashboard_data(config)

    assert isinstance(dashboard_data, DashboardData)
    assert not dashboard_data.raw_events.empty
    assert dashboard_data.session_summary["total_players"] == 4
    assert dashboard_data.session_summary["total_sessions"] >= 4
    assert not dashboard_data.level_performance.empty
    assert "player_deaths" in dashboard_data.combat_summary
    assert "enemy_defeats" in dashboard_data.combat_summary
