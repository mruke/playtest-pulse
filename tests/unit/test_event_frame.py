from __future__ import annotations

import pandas as pd
import pytest

from playtest_pulse.analytics.event_frame import events_to_frame
from playtest_pulse.domain import RAW_EVENT_COLUMNS
from playtest_pulse.domain import EventTypes, TelemetryEvent


# ---------------------------------------------------------------------------
# _event
#
# Builds a valid TelemetryEvent for DataFrame conversion tests.
# ---------------------------------------------------------------------------
def _event(
    event_id: str = "event-001",
    event_type: str = EventTypes.SESSION_START,
    timestamp: str = "2026-01-01T12:00:00",
) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=event_id,
        player_id="player-001",
        session_id="session-001",
        timestamp=timestamp,
        event_type=event_type,
        level_id="level-001",
        enemy_type=None,
        item_id=None,
        duration_seconds=None,
        damage_taken=None,
        result=None,
    )


# ---------------------------------------------------------------------------
# test_events_to_frame_returns_dataframe
#
# Verifies that valid telemetry events are converted into a pandas DataFrame.
# ---------------------------------------------------------------------------
def test_events_to_frame_returns_dataframe() -> None:
    frame = events_to_frame([_event()])

    assert isinstance(frame, pd.DataFrame)


# ---------------------------------------------------------------------------
# test_events_to_frame_includes_expected_columns
#
# Verifies that the DataFrame contains the expected raw event columns.
# ---------------------------------------------------------------------------
def test_events_to_frame_includes_expected_columns() -> None:
    frame = events_to_frame([_event()])

    assert list(frame.columns) == RAW_EVENT_COLUMNS


# ---------------------------------------------------------------------------
# test_events_to_frame_preserves_event_order
#
# Verifies that event row order matches the input event order.
# ---------------------------------------------------------------------------
def test_events_to_frame_preserves_event_order() -> None:
    events = [
        _event(event_id="event-001"),
        _event(event_id="event-002"),
        _event(event_id="event-003"),
    ]

    frame = events_to_frame(events)

    assert frame["event_id"].tolist() == [
        "event-001",
        "event-002",
        "event-003",
    ]


# ---------------------------------------------------------------------------
# test_events_to_frame_parses_timestamp_column
#
# Verifies that timestamp strings are converted into pandas datetime values.
# ---------------------------------------------------------------------------
def test_events_to_frame_parses_timestamp_column() -> None:
    frame = events_to_frame([_event()])

    assert pd.api.types.is_datetime64_any_dtype(frame["timestamp"])


# ---------------------------------------------------------------------------
# test_events_to_frame_preserves_optional_values
#
# Verifies that optional event values are preserved in the DataFrame.
# ---------------------------------------------------------------------------
def test_events_to_frame_preserves_optional_values() -> None:
    event = TelemetryEvent(
        event_id="event-001",
        player_id="player-001",
        session_id="session-001",
        timestamp="2026-01-01T12:00:00",
        event_type=EventTypes.ENEMY_DEFEATED,
        level_id="level-001",
        enemy_type="slime",
        item_id=None,
        duration_seconds=10,
        damage_taken=3,
        result="success",
    )

    frame = events_to_frame([event])

    assert frame.loc[0, "level_id"] == "level-001"
    assert frame.loc[0, "enemy_type"] == "slime"
    assert pd.isna(frame.loc[0, "item_id"])
    assert frame.loc[0, "duration_seconds"] == 10
    assert frame.loc[0, "damage_taken"] == 3
    assert frame.loc[0, "result"] == "success"


# ---------------------------------------------------------------------------
# test_events_to_frame_rejects_empty_events
#
# Verifies that an empty event list is rejected.
# ---------------------------------------------------------------------------
def test_events_to_frame_rejects_empty_events() -> None:
    with pytest.raises(ValueError, match="at least one"):
        events_to_frame([])


# ---------------------------------------------------------------------------
# test_events_to_frame_rejects_non_event_values
#
# Verifies that every input value must be a TelemetryEvent.
# ---------------------------------------------------------------------------
def test_events_to_frame_rejects_non_event_values() -> None:
    with pytest.raises(TypeError, match="TelemetryEvent"):
        events_to_frame([object()])  # type: ignore[list-item]


# ---------------------------------------------------------------------------
# test_events_to_frame_rejects_invalid_timestamp
#
# Verifies that invalid timestamp values fail during DataFrame conversion.
# ---------------------------------------------------------------------------
def test_events_to_frame_rejects_invalid_timestamp() -> None:
    event = _event(timestamp="not-a-timestamp")

    with pytest.raises(ValueError):
        events_to_frame([event])
