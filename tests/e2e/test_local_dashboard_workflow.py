from __future__ import annotations

from pathlib import Path

from playtest_pulse.dashboard import DashboardData, load_dashboard_data
from playtest_pulse.ingestion import generate_sample_events, load_events_csv
from playtest_pulse.storage import TelemetryRepository
from tests.helpers.config_factories import make_app_config
from tests.helpers.io_helpers import write_events_csv


# ---------------------------------------------------------------------------
# _write_sample_csv
#
# Generates sample telemetry and writes it to the configured CSV path.
# ---------------------------------------------------------------------------
def _write_sample_csv(tmp_path: Path) -> None:
    config = make_app_config(tmp_path)
    events = generate_sample_events(
        project_config=config.project,
        generation_config=config.generation,
    )

    write_events_csv(Path(config.data.raw_events_path), events)


# ---------------------------------------------------------------------------
# _ingest_events
#
# Loads generated CSV events and stores them in local SQLite storage.
# ---------------------------------------------------------------------------
def _ingest_events(tmp_path: Path) -> None:
    config = make_app_config(tmp_path)
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
    config = make_app_config(tmp_path)

    _write_sample_csv(tmp_path)
    _ingest_events(tmp_path)

    dashboard_data = load_dashboard_data(config)

    assert isinstance(dashboard_data, DashboardData)
    assert not dashboard_data.raw_events.empty
    assert (
        dashboard_data.session_summary["total_players"]
        == config.generation.player_count
    )
    assert (
        dashboard_data.session_summary["total_sessions"]
        >= config.generation.player_count
    )
    assert not dashboard_data.level_performance.empty
    assert "player_deaths" in dashboard_data.combat_summary
    assert "enemy_defeats" in dashboard_data.combat_summary
