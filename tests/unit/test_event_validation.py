from __future__ import annotations

import pytest

from playtest_pulse.domain import EventTypes, TelemetryEvent
from playtest_pulse.ingestion.event_validation import validate_raw_event_row


# ---------------------------------------------------------------------------
# _valid_raw_event_row
#
# Builds a valid raw CSV event row for validation tests.
# ---------------------------------------------------------------------------
def _valid_raw_event_row(**overrides: str) -> dict[str, str]:
    row = {
        "event_id": "event-001",
        "player_id": "player-001",
        "session_id": "session-001",
        "timestamp": "2026-01-01T12:00:00",
        "event_type": EventTypes.LEVEL_COMPLETE,
        "level_id": "level-001",
        "enemy_type": "",
        "item_id": "",
        "duration_seconds": "120",
        "damage_taken": "5",
        "result": "success",
    }
    row.update(overrides)

    return row


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_returns_telemetry_event
#
# Verifies that a valid raw CSV event row becomes a TelemetryEvent.
# ---------------------------------------------------------------------------
def test_validate_raw_event_row_returns_telemetry_event() -> None:
    event = validate_raw_event_row(_valid_raw_event_row())

    assert isinstance(event, TelemetryEvent)
    assert event.event_id == "event-001"
    assert event.player_id == "player-001"
    assert event.session_id == "session-001"
    assert event.event_type == EventTypes.LEVEL_COMPLETE
    assert event.level_id == "level-001"
    assert event.duration_seconds == 120
    assert event.damage_taken == 5
    assert event.result == "success"


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_converts_empty_optional_fields_to_none
#
# Verifies that empty optional CSV fields become None values.
# ---------------------------------------------------------------------------
def test_validate_raw_event_row_converts_empty_optional_fields_to_none() -> None:
    event = validate_raw_event_row(
        _valid_raw_event_row(
            level_id="",
            enemy_type="",
            item_id="",
            duration_seconds="",
            damage_taken="",
            result="",
        )
    )

    assert event.level_id is None
    assert event.enemy_type is None
    assert event.item_id is None
    assert event.duration_seconds is None
    assert event.damage_taken is None
    assert event.result is None


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_rejects_missing_column
#
# Verifies that raw CSV rows must contain all expected event columns.
# ---------------------------------------------------------------------------
def test_validate_raw_event_row_rejects_missing_column() -> None:
    row = _valid_raw_event_row()
    del row["event_id"]

    with pytest.raises(ValueError, match="event_id"):
        validate_raw_event_row(row)


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_rejects_empty_required_text
#
# Verifies that required text fields cannot be empty.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "column",
    [
        "event_id",
        "player_id",
        "session_id",
        "timestamp",
        "event_type",
    ],
)
def test_validate_raw_event_row_rejects_empty_required_text(column: str) -> None:
    with pytest.raises(ValueError, match=column):
        validate_raw_event_row(_valid_raw_event_row(**{column: ""}))


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_rejects_unsupported_event_type
#
# Verifies that event_type must use one of the supported event names.
# ---------------------------------------------------------------------------
def test_validate_raw_event_row_rejects_unsupported_event_type() -> None:
    with pytest.raises(ValueError, match="Unsupported event type"):
        validate_raw_event_row(_valid_raw_event_row(event_type="bad_event"))


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_rejects_non_integer_numeric_field
#
# Verifies that numeric CSV fields must parse as integers when provided.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "column",
    [
        "duration_seconds",
        "damage_taken",
    ],
)
def test_validate_raw_event_row_rejects_non_integer_numeric_field(column: str) -> None:
    with pytest.raises(ValueError, match=column):
        validate_raw_event_row(_valid_raw_event_row(**{column: "not-a-number"}))


# ---------------------------------------------------------------------------
# test_validate_raw_event_row_rejects_negative_numeric_field
#
# Verifies that numeric CSV fields must be non-negative when provided.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "column",
    [
        "duration_seconds",
        "damage_taken",
    ],
)
def test_validate_raw_event_row_rejects_negative_numeric_field(column: str) -> None:
    with pytest.raises(ValueError, match=column):
        validate_raw_event_row(_valid_raw_event_row(**{column: "-1"}))
