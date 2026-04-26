from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

import pytest

from playtest_pulse.config import GenerationConfig, ProjectConfig
from playtest_pulse.domain import TelemetryEvent
from playtest_pulse.ingestion import generate_sample_events, load_events_csv
from playtest_pulse.domain import RAW_EVENT_COLUMNS


# ---------------------------------------------------------------------------
# _write_rows
#
# Writes raw telemetry rows to a temporary CSV file for loader tests.
# ---------------------------------------------------------------------------
def _write_rows(tmp_path: Path, rows: list[dict[str, object]]) -> Path:
    csv_path = tmp_path / "events.csv"
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
        writer = csv.DictWriter(csv_file, fieldnames=RAW_EVENT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


# ---------------------------------------------------------------------------
# _sample_rows
#
# Builds sample rows by generating real sample events and converting to dicts.
# ---------------------------------------------------------------------------
def _sample_rows() -> list[dict[str, object]]:
    events = generate_sample_events(
        project_config=ProjectConfig(
            name="playtest-pulse",
            version="0.1.0",
            seed=42,
        ),
        generation_config=GenerationConfig(
            player_count=3,
            min_sessions_per_player=1,
            max_sessions_per_player=2,
            level_count=3,
        ),
    )

    return [asdict(event) for event in events]


# ---------------------------------------------------------------------------
# test_load_events_csv_returns_events
#
# Verifies that a valid telemetry CSV file loads into TelemetryEvent objects.
# ---------------------------------------------------------------------------
def test_load_events_csv_returns_events(tmp_path: Path) -> None:
    csv_path = _write_rows(tmp_path, _sample_rows())

    events = load_events_csv(csv_path)

    assert events
    assert all(isinstance(event, TelemetryEvent) for event in events)


# ---------------------------------------------------------------------------
# test_load_events_csv_preserves_event_order
#
# Verifies that loaded events preserve the order from the CSV file.
# ---------------------------------------------------------------------------
def test_load_events_csv_preserves_event_order(tmp_path: Path) -> None:
    rows = _sample_rows()
    csv_path = _write_rows(tmp_path, rows)

    events = load_events_csv(csv_path)

    assert [event.event_id for event in events] == [
        str(row["event_id"]) for row in rows
    ]


# ---------------------------------------------------------------------------
# test_load_events_csv_rejects_missing_file
#
# Verifies that loading a missing CSV file fails clearly.
# ---------------------------------------------------------------------------
def test_load_events_csv_rejects_missing_file() -> None:
    with pytest.raises(FileNotFoundError, match="does not exist"):
        load_events_csv("data/raw/does-not-exist.csv")


# ---------------------------------------------------------------------------
# test_load_events_csv_rejects_empty_file
#
# Verifies that a CSV file with no header row fails clearly.
# ---------------------------------------------------------------------------
def test_load_events_csv_rejects_empty_file(tmp_path: Path) -> None:
    csv_path = tmp_path / "empty.csv"
    csv_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="no header row"):
        load_events_csv(csv_path)


# ---------------------------------------------------------------------------
# test_load_events_csv_reports_invalid_row_number
#
# Verifies that invalid rows report their CSV row number.
# ---------------------------------------------------------------------------
def test_load_events_csv_reports_invalid_row_number(tmp_path: Path) -> None:
    rows = _sample_rows()
    rows[1]["event_type"] = "bad_event"
    csv_path = _write_rows(tmp_path, rows)

    with pytest.raises(ValueError, match="row 3"):
        load_events_csv(csv_path)
