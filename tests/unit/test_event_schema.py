from __future__ import annotations

import pytest

from playtest_pulse.domain import EventTypes, TelemetryEvent


# ---------------------------------------------------------------------------
# _valid_event
#
# Builds a valid telemetry event for focused schema tests.
# ---------------------------------------------------------------------------
def _valid_event(**overrides: object) -> TelemetryEvent:
    values = {
        "event_id": "event-001",
        "player_id": "player-001",
        "session_id": "session-001",
        "timestamp": "2026-01-01T12:00:00",
        "event_type": EventTypes.SESSION_START,
        "level_id": None,
        "enemy_type": None,
        "item_id": None,
        "duration_seconds": None,
        "damage_taken": None,
        "result": None,
    }
    values.update(overrides)

    return TelemetryEvent(**values)


# ---------------------------------------------------------------------------
# test_valid_event_can_be_created
#
# Verifies that a complete valid telemetry event can be created.
# ---------------------------------------------------------------------------
def test_valid_event_can_be_created() -> None:
    event = _valid_event()

    assert event.event_id == "event-001"
    assert event.player_id == "player-001"
    assert event.session_id == "session-001"
    assert event.timestamp == "2026-01-01T12:00:00"
    assert event.event_type == EventTypes.SESSION_START


# ---------------------------------------------------------------------------
# test_event_types_include_expected_values
#
# Verifies that the supported event type set includes the planned event names.
# ---------------------------------------------------------------------------
def test_event_types_include_expected_values() -> None:
    assert EventTypes.ALL == {
        "session_start",
        "session_end",
        "level_start",
        "level_complete",
        "level_fail",
        "player_death",
        "item_pickup",
        "enemy_defeated",
    }


# ---------------------------------------------------------------------------
# test_event_rejects_empty_required_string
#
# Verifies that required ID and timestamp fields cannot be empty.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "field_name",
    [
        "event_id",
        "player_id",
        "session_id",
        "timestamp",
    ],
)
def test_event_rejects_empty_required_string(field_name: str) -> None:
    with pytest.raises(ValueError, match=field_name):
        _valid_event(**{field_name: ""})


# ---------------------------------------------------------------------------
# test_event_rejects_invalid_event_type
#
# Verifies that event_type must be one of the supported event names.
# ---------------------------------------------------------------------------
def test_event_rejects_invalid_event_type() -> None:
    with pytest.raises(ValueError, match="Unsupported event type"):
        _valid_event(event_type="unknown_event")


# ---------------------------------------------------------------------------
# test_event_accepts_optional_context_fields
#
# Verifies that optional event context fields can be included.
# ---------------------------------------------------------------------------
def test_event_accepts_optional_context_fields() -> None:
    event = _valid_event(
        event_type=EventTypes.ENEMY_DEFEATED,
        level_id="level-01",
        enemy_type="slime",
        item_id="health_potion",
        duration_seconds=12,
        damage_taken=4,
        result="success",
    )

    assert event.level_id == "level-01"
    assert event.enemy_type == "slime"
    assert event.item_id == "health_potion"
    assert event.duration_seconds == 12
    assert event.damage_taken == 4
    assert event.result == "success"


# ---------------------------------------------------------------------------
# test_event_rejects_negative_duration
#
# Verifies that duration_seconds cannot be negative when provided.
# ---------------------------------------------------------------------------
def test_event_rejects_negative_duration() -> None:
    with pytest.raises(ValueError, match="duration_seconds"):
        _valid_event(duration_seconds=-1)


# ---------------------------------------------------------------------------
# test_event_rejects_negative_damage_taken
#
# Verifies that damage_taken cannot be negative when provided.
# ---------------------------------------------------------------------------
def test_event_rejects_negative_damage_taken() -> None:
    with pytest.raises(ValueError, match="damage_taken"):
        _valid_event(damage_taken=-1)


# ---------------------------------------------------------------------------
# test_event_rejects_non_integer_optional_numeric_fields
#
# Verifies that optional numeric fields must be integers when provided.
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "field_name",
    [
        "duration_seconds",
        "damage_taken",
    ],
)
def test_event_rejects_non_integer_optional_numeric_fields(
    field_name: str,
) -> None:
    with pytest.raises(ValueError, match=field_name):
        _valid_event(**{field_name: "1"})
