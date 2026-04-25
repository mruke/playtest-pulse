from __future__ import annotations

from playtest_pulse.domain import EventTypes, TelemetryEvent


RAW_EVENT_COLUMNS = [
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
# validate_raw_event_row
#
# Validates one raw CSV event row and converts it into a TelemetryEvent.
# ---------------------------------------------------------------------------
def validate_raw_event_row(row: dict[str, str]) -> TelemetryEvent:
    _validate_raw_event_columns(row)

    return TelemetryEvent(
        event_id=_required_text(row, "event_id"),
        player_id=_required_text(row, "player_id"),
        session_id=_required_text(row, "session_id"),
        timestamp=_required_text(row, "timestamp"),
        event_type=_required_event_type(row),
        level_id=_optional_text(row, "level_id"),
        enemy_type=_optional_text(row, "enemy_type"),
        item_id=_optional_text(row, "item_id"),
        duration_seconds=_optional_integer(row, "duration_seconds"),
        damage_taken=_optional_integer(row, "damage_taken"),
        result=_optional_text(row, "result"),
    )


# ---------------------------------------------------------------------------
# _validate_raw_event_columns
#
# Verifies that a raw CSV event row contains every expected column.
# ---------------------------------------------------------------------------
def _validate_raw_event_columns(row: dict[str, str]) -> None:
    missing_columns = [column for column in RAW_EVENT_COLUMNS if column not in row]

    if missing_columns:
        joined_columns = ", ".join(missing_columns)
        raise ValueError(f"Missing raw event columns: {joined_columns}")


# ---------------------------------------------------------------------------
# _required_text
#
# Reads a required non-empty text value from a raw CSV event row.
# ---------------------------------------------------------------------------
def _required_text(row: dict[str, str], column: str) -> str:
    value = row[column].strip()

    if not value:
        raise ValueError(f"{column} must be a non-empty string.")

    return value


# ---------------------------------------------------------------------------
# _optional_text
#
# Reads an optional text value from a raw CSV event row.
# ---------------------------------------------------------------------------
def _optional_text(row: dict[str, str], column: str) -> str | None:
    value = row[column].strip()

    if not value:
        return None

    return value


# ---------------------------------------------------------------------------
# _required_event_type
#
# Reads and validates the event type from a raw CSV event row.
# ---------------------------------------------------------------------------
def _required_event_type(row: dict[str, str]) -> str:
    event_type = _required_text(row, "event_type")

    if event_type not in EventTypes.ALL:
        raise ValueError(f"Unsupported event type: {event_type}")

    return event_type


# ---------------------------------------------------------------------------
# _optional_integer
#
# Reads an optional non-negative integer from a raw CSV event row.
# ---------------------------------------------------------------------------
def _optional_integer(row: dict[str, str], column: str) -> int | None:
    value = row[column].strip()

    if not value:
        return None

    try:
        parsed_value = int(value)
    except ValueError as error:
        raise ValueError(f"{column} must be an integer.") from error

    if parsed_value < 0:
        raise ValueError(f"{column} must be non-negative.")

    return parsed_value
