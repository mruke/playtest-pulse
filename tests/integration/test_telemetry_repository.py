from __future__ import annotations

from pathlib import Path

import pytest

from playtest_pulse.domain import EventTypes, TelemetryEvent
from playtest_pulse.storage import TelemetryRepository


# ---------------------------------------------------------------------------
# _event
#
# Builds a valid telemetry event for repository tests.
# ---------------------------------------------------------------------------
def _event(
    event_id: str = "event-001",
    event_type: str = EventTypes.SESSION_START,
    level_id: str | None = None,
    enemy_type: str | None = None,
    item_id: str | None = None,
    duration_seconds: int | None = None,
    damage_taken: int | None = None,
    result: str | None = None,
) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=event_id,
        player_id="player-001",
        session_id="session-001",
        timestamp="2026-01-01T12:00:00",
        event_type=event_type,
        level_id=level_id,
        enemy_type=enemy_type,
        item_id=item_id,
        duration_seconds=duration_seconds,
        damage_taken=damage_taken,
        result=result,
    )


# ---------------------------------------------------------------------------
# _repository
#
# Creates a repository backed by a temporary SQLite database file.
# ---------------------------------------------------------------------------
def _repository(tmp_path: Path) -> TelemetryRepository:
    return TelemetryRepository(tmp_path / "telemetry.sqlite3")


# ---------------------------------------------------------------------------
# test_repository_creates_database_file
#
# Verifies that opening the repository creates a local SQLite database.
# ---------------------------------------------------------------------------
def test_repository_creates_database_file(tmp_path: Path) -> None:
    database_path = tmp_path / "telemetry.sqlite3"

    repository = TelemetryRepository(database_path)
    repository.close()

    assert database_path.exists()


# ---------------------------------------------------------------------------
# test_insert_events_rejects_empty_event_list
#
# Verifies that inserts require at least one telemetry event.
# ---------------------------------------------------------------------------
def test_insert_events_rejects_empty_event_list(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    with pytest.raises(ValueError, match="at least one"):
        repository.insert_events([])

    repository.close()


# ---------------------------------------------------------------------------
# test_insert_events_writes_base_events
#
# Verifies that inserted events appear in the base events table.
# ---------------------------------------------------------------------------
def test_insert_events_writes_base_events(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            _event(event_id="event-001"),
            _event(event_id="event-002", event_type=EventTypes.SESSION_END),
        ]
    )

    rows = repository.connection.execute(
        "SELECT event_id, event_type FROM events ORDER BY event_id;"
    ).fetchall()
    repository.close()

    assert [dict(row) for row in rows] == [
        {
            "event_id": "event-001",
            "event_type": EventTypes.SESSION_START,
        },
        {
            "event_id": "event-002",
            "event_type": EventTypes.SESSION_END,
        },
    ]


# ---------------------------------------------------------------------------
# test_insert_events_writes_level_event_details
#
# Verifies that level-related events write to level_events.
# ---------------------------------------------------------------------------
def test_insert_events_writes_level_event_details(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            _event(
                event_id="event-001",
                event_type=EventTypes.LEVEL_COMPLETE,
                level_id="level-001",
                duration_seconds=120,
                result="success",
            )
        ]
    )

    row = repository.connection.execute(
        "SELECT event_id, level_id, result, duration_seconds FROM level_events;"
    ).fetchone()
    repository.close()

    assert dict(row) == {
        "event_id": "event-001",
        "level_id": "level-001",
        "result": "success",
        "duration_seconds": 120,
    }


# ---------------------------------------------------------------------------
# test_insert_events_writes_combat_event_details
#
# Verifies that combat-related events write to combat_events.
# ---------------------------------------------------------------------------
def test_insert_events_writes_combat_event_details(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            _event(
                event_id="event-001",
                event_type=EventTypes.ENEMY_DEFEATED,
                level_id="level-001",
                enemy_type="slime",
                damage_taken=5,
                result="success",
            )
        ]
    )

    row = repository.connection.execute(
        "SELECT event_id, enemy_type, damage_taken, result FROM combat_events;"
    ).fetchone()
    repository.close()

    assert dict(row) == {
        "event_id": "event-001",
        "enemy_type": "slime",
        "damage_taken": 5,
        "result": "success",
    }


# ---------------------------------------------------------------------------
# test_insert_events_writes_item_event_details
#
# Verifies that item pickup events write to item_events.
# ---------------------------------------------------------------------------
def test_insert_events_writes_item_event_details(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            _event(
                event_id="event-001",
                event_type=EventTypes.ITEM_PICKUP,
                level_id="level-001",
                item_id="health_potion",
            )
        ]
    )

    row = repository.connection.execute(
        "SELECT event_id, item_id FROM item_events;"
    ).fetchone()
    repository.close()

    assert dict(row) == {
        "event_id": "event-001",
        "item_id": "health_potion",
    }


# ---------------------------------------------------------------------------
# test_count_events_returns_inserted_event_count
#
# Verifies that count_events returns the number of stored base event rows.
# ---------------------------------------------------------------------------
def test_count_events_returns_inserted_event_count(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            _event(event_id="event-001"),
            _event(event_id="event-002", event_type=EventTypes.SESSION_END),
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
            _event(event_id="event-001"),
            _event(
                event_id="event-002",
                event_type=EventTypes.LEVEL_COMPLETE,
                level_id="level-001",
                duration_seconds=120,
                result="success",
            ),
            _event(
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
# test_fetch_events_frame_parses_timestamp_column
#
# Verifies that fetched events use pandas datetime values for timestamps.
# ---------------------------------------------------------------------------
def test_fetch_events_frame_parses_timestamp_column(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events([_event()])

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

    repository.insert_events([_event()])

    frame = repository.fetch_events_frame()
    repository.close()

    assert list(frame.columns) == [
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
