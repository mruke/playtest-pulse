from __future__ import annotations

from pathlib import Path

import pytest

from playtest_pulse.domain import EventTypes
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
            make_event(event_id="event-001"),
            make_event(event_id="event-002", event_type=EventTypes.SESSION_END),
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
# test_insert_events_writes_session_event_details
#
# Verifies that session end events write session duration details.
# ---------------------------------------------------------------------------
def test_insert_events_writes_session_event_details(tmp_path: Path) -> None:
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

    row = repository.connection.execute(
        "SELECT event_id, duration_seconds FROM session_events;"
    ).fetchone()
    repository.close()

    assert dict(row) == {
        "event_id": "event-001",
        "duration_seconds": 300,
    }


# ---------------------------------------------------------------------------
# test_insert_events_writes_level_event_details
#
# Verifies that level-related events write to level_events.
# ---------------------------------------------------------------------------
def test_insert_events_writes_level_event_details(tmp_path: Path) -> None:
    repository = _repository(tmp_path)

    repository.insert_events(
        [
            make_event(
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
            make_event(
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
            make_event(
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
