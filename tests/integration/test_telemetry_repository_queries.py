from __future__ import annotations

from pathlib import Path

from playtest_pulse.domain import EventTypes, RAW_EVENT_COLUMNS
from playtest_pulse.storage import TelemetryRepository
from tests.helpers.event_factories import make_event


# ---------------------------------------------------------------------------
# _repository
#
# Creates a repository backed by a temporary SQLite database file.
# ---------------------------------------------------------------------------
def _repository(tmp_path: Path) -> TelemetryRepository:
    return TelemetryRepository(tmp_path / "telemetry.sqlite3")


# ---------------------------------------------------------------------------
# test_count_events_returns_inserted_event_count
#
# Verifies that count_events returns the number of stored base event rows.
# ---------------------------------------------------------------------------
def test_count_events_returns_inserted_event_count(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            make_event(event_id="event-001"),
            make_event(event_id="event-002", event_type=EventTypes.SESSION_END),
        ]
    )

    count = repository.count_events()
    repository.close()

    assert count == 2


# ---------------------------------------------------------------------------
# test_fetch_events_frame_returns_stored_events
#
# Verifies that stored normalized events can be read back as a DataFrame.
# ---------------------------------------------------------------------------
def test_fetch_events_frame_returns_stored_events(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            make_event(event_id="event-001"),
            make_event(
                event_id="event-002",
                event_type=EventTypes.LEVEL_COMPLETE,
                level_id="level-001",
                duration_seconds=120,
                result="success",
            ),
            make_event(
                event_id="event-003",
                event_type=EventTypes.ITEM_PICKUP,
                level_id="level-001",
                item_id="health_potion",
            ),
        ]
    )

    frame = repository.fetch_events_frame()
    repository.close()

    assert frame["event_id"].tolist() == [
        "event-001",
        "event-002",
        "event-003",
    ]
    assert frame.loc[1, "level_id"] == "level-001"
    assert frame.loc[1, "duration_seconds"] == 120
    assert frame.loc[1, "result"] == "success"
    assert frame.loc[2, "item_id"] == "health_potion"


# ---------------------------------------------------------------------------
# test_fetch_events_frame_preserves_session_duration
#
# Verifies that fetched DataFrames include session end duration values.
# ---------------------------------------------------------------------------
def test_fetch_events_frame_preserves_session_duration(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            make_event(
                event_id="event-001",
                event_type=EventTypes.SESSION_END,
                duration_seconds=300,
            )
        ]
    )

    frame = repository.fetch_events_frame()
    repository.close()

    assert frame.loc[0, "duration_seconds"] == 300


# ---------------------------------------------------------------------------
# test_fetch_events_frame_parses_timestamp_column
#
# Verifies that fetched events use pandas datetime values for timestamps.
# ---------------------------------------------------------------------------
def test_fetch_events_frame_parses_timestamp_column(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events([make_event()])

    frame = repository.fetch_events_frame()
    repository.close()

    assert str(frame["timestamp"].dtype).startswith("datetime64")


# ---------------------------------------------------------------------------
# test_fetch_events_frame_returns_expected_columns
#
# Verifies that fetched event DataFrames match the analytics event shape.
# ---------------------------------------------------------------------------
def test_fetch_events_frame_returns_expected_columns(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events([make_event()])

    frame = repository.fetch_events_frame()
    repository.close()

    assert list(frame.columns) == RAW_EVENT_COLUMNS
