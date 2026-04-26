from __future__ import annotations

from playtest_pulse.domain import EventTypes, TelemetryEvent


# ---------------------------------------------------------------------------
# make_event
#
# Builds a valid telemetry event for tests.
# ---------------------------------------------------------------------------
def make_event(
    event_id: str = "event-001",
    event_type: str = EventTypes.SESSION_START,
    player_id: str = "player-001",
    session_id: str = "session-001",
    timestamp: str = "2026-01-01T12:00:00",
    level_id: str | None = None,
    enemy_type: str | None = None,
    item_id: str | None = None,
    duration_seconds: int | None = None,
    damage_taken: int | None = None,
    result: str | None = None,
) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=event_id,
        player_id=player_id,
        session_id=session_id,
        timestamp=timestamp,
        event_type=event_type,
        level_id=level_id,
        enemy_type=enemy_type,
        item_id=item_id,
        duration_seconds=duration_seconds,
        damage_taken=damage_taken,
        result=result,
    )
