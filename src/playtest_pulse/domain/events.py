from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


# ---------------------------------------------------------------------------
# EventTypes
#
# Defines the supported event type names for simulated playtest telemetry.
# ---------------------------------------------------------------------------
class EventTypes:
    SESSION_START: ClassVar[str] = "session_start"
    SESSION_END: ClassVar[str] = "session_end"
    LEVEL_START: ClassVar[str] = "level_start"
    LEVEL_COMPLETE: ClassVar[str] = "level_complete"
    LEVEL_FAIL: ClassVar[str] = "level_fail"
    PLAYER_DEATH: ClassVar[str] = "player_death"
    ITEM_PICKUP: ClassVar[str] = "item_pickup"
    ENEMY_DEFEATED: ClassVar[str] = "enemy_defeated"

    ALL: ClassVar[set[str]] = {
        SESSION_START,
        SESSION_END,
        LEVEL_START,
        LEVEL_COMPLETE,
        LEVEL_FAIL,
        PLAYER_DEATH,
        ITEM_PICKUP,
        ENEMY_DEFEATED,
    }


# ---------------------------------------------------------------------------
# TelemetryEvent
#
# Stores one simulated playtest telemetry event.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class TelemetryEvent:
    event_id: str
    player_id: str
    session_id: str
    timestamp: str
    event_type: str
    level_id: str | None = None
    enemy_type: str | None = None
    item_id: str | None = None
    duration_seconds: int | None = None
    damage_taken: int | None = None
    result: str | None = None

    # -----------------------------------------------------------------------
    # __post_init__
    #
    # Validates event values after dataclass construction.
    # -----------------------------------------------------------------------
    def __post_init__(self) -> None:
        _require_non_empty_string(self.event_id, "event_id")
        _require_non_empty_string(self.player_id, "player_id")
        _require_non_empty_string(self.session_id, "session_id")
        _require_non_empty_string(self.timestamp, "timestamp")

        if self.event_type not in EventTypes.ALL:
            raise ValueError(f"Unsupported event type: {self.event_type}")

        _validate_optional_non_negative_integer(
            self.duration_seconds,
            "duration_seconds",
        )
        _validate_optional_non_negative_integer(
            self.damage_taken,
            "damage_taken",
        )


# ---------------------------------------------------------------------------
# _require_non_empty_string
#
# Validates that a required value is a non-empty string.
# ---------------------------------------------------------------------------
def _require_non_empty_string(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field_name} must be a non-empty string.")


# ---------------------------------------------------------------------------
# _validate_optional_non_negative_integer
#
# Validates that an optional numeric value is either missing or non-negative.
# ---------------------------------------------------------------------------
def _validate_optional_non_negative_integer(
    value: int | None,
    field_name: str,
) -> None:
    if value is None:
        return

    if not isinstance(value, int) or value < 0:
        raise ValueError(f"{field_name} must be a non-negative integer.")
