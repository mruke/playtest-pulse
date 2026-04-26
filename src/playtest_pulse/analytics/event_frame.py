from __future__ import annotations

from dataclasses import asdict

import pandas as pd

from playtest_pulse.domain import TelemetryEvent


EVENT_FRAME_COLUMNS = [
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


# ---------------------------------------------------------------------------
# events_to_frame
#
# Converts validated telemetry events into a pandas DataFrame for analytics.
# ---------------------------------------------------------------------------
def events_to_frame(events: list[TelemetryEvent]) -> pd.DataFrame:
    if not events:
        raise ValueError("events must contain at least one TelemetryEvent.")

    _validate_events(events)

    frame = pd.DataFrame([asdict(event) for event in events])
    frame = frame[EVENT_FRAME_COLUMNS]
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")

    return frame


# ---------------------------------------------------------------------------
# _validate_events
#
# Verifies that every input value is a TelemetryEvent before conversion.
# ---------------------------------------------------------------------------
def _validate_events(events: list[TelemetryEvent]) -> None:
    for event in events:
        if not isinstance(event, TelemetryEvent):
            raise TypeError("events must contain only TelemetryEvent objects.")
