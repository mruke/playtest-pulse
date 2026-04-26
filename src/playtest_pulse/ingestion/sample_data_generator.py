from __future__ import annotations

from datetime import datetime, timedelta
import random

from playtest_pulse.config import GenerationConfig, ProjectConfig
from playtest_pulse.domain import EventTypes, TelemetryEvent


SIMULATION_START_TIME = datetime(2026, 1, 1, 12, 0, 0)

PLAYER_SESSION_OFFSET_MINUTES = 10

MIN_SECONDS_BEFORE_LEVEL_START = 15
MAX_SECONDS_BEFORE_LEVEL_START = 90

MIN_SECONDS_BEFORE_LEVEL_OUTCOME = 20
MAX_SECONDS_BEFORE_LEVEL_OUTCOME = 180

MIN_LEVEL_DURATION_SECONDS = 30
MAX_LEVEL_DURATION_SECONDS = 240

MIN_SECONDS_BEFORE_SESSION_END = 10
MAX_SECONDS_BEFORE_SESSION_END = 60

MIN_OPTIONAL_EVENTS_PER_LEVEL = 0
MAX_OPTIONAL_EVENTS_PER_LEVEL = 3

MIN_SECONDS_BETWEEN_OPTIONAL_EVENTS = 5
MAX_SECONDS_BETWEEN_OPTIONAL_EVENTS = 45

MIN_ENEMY_DAMAGE_TAKEN = 0
MAX_ENEMY_DAMAGE_TAKEN = 20

MIN_PLAYER_DEATH_DAMAGE_TAKEN = 1
MAX_PLAYER_DEATH_DAMAGE_TAKEN = 30

LEVEL_OUTCOMES = [
    EventTypes.LEVEL_COMPLETE,
    EventTypes.LEVEL_FAIL,
]

OPTIONAL_EVENT_TYPES = [
    EventTypes.ITEM_PICKUP,
    EventTypes.ENEMY_DEFEATED,
    EventTypes.PLAYER_DEATH,
]

ITEM_IDS = [
    "health_potion",
    "mana_potion",
    "iron_key",
    "gold_coin",
]

ENEMY_TYPES = [
    "slime",
    "goblin",
    "skeleton",
    "wolf",
]


# ---------------------------------------------------------------------------
# generate_sample_events
#
# Generates deterministic simulated playtest telemetry events.
# ---------------------------------------------------------------------------
def generate_sample_events(
    project_config: ProjectConfig,
    generation_config: GenerationConfig,
) -> list[TelemetryEvent]:
    rng = random.Random(project_config.seed)
    events: list[TelemetryEvent] = []
    event_number = 1

    for player_number in range(1, generation_config.player_count + 1):
        player_id = _format_id("player", player_number)
        session_count = rng.randint(
            generation_config.min_sessions_per_player,
            generation_config.max_sessions_per_player,
        )

        for session_number in range(1, session_count + 1):
            session_id = f"{player_id}-session-{session_number:03d}"
            session_start = SIMULATION_START_TIME + timedelta(
                minutes=(player_number * PLAYER_SESSION_OFFSET_MINUTES)
                + session_number,
            )

            session_events, event_number = _generate_session_events(
                rng=rng,
                event_number=event_number,
                player_id=player_id,
                session_id=session_id,
                session_start=session_start,
                level_count=generation_config.level_count,
            )
            events.extend(session_events)

    return events


# ---------------------------------------------------------------------------
# _generate_session_events
#
# Generates the event sequence for one simulated playtest session.
# ---------------------------------------------------------------------------
def _generate_session_events(
    rng: random.Random,
    event_number: int,
    player_id: str,
    session_id: str,
    session_start: datetime,
    level_count: int,
) -> tuple[list[TelemetryEvent], int]:
    events: list[TelemetryEvent] = []

    events.append(
        _build_event(
            event_number=event_number,
            player_id=player_id,
            session_id=session_id,
            timestamp=session_start,
            event_type=EventTypes.SESSION_START,
        )
    )
    event_number += 1

    levels_attempted = rng.randint(1, level_count)
    current_time = session_start

    for level_number in range(1, levels_attempted + 1):
        level_id = _format_id("level", level_number)
        current_time += timedelta(
            seconds=rng.randint(
                MIN_SECONDS_BEFORE_LEVEL_START,
                MAX_SECONDS_BEFORE_LEVEL_START,
            )
        )

        events.append(
            _build_event(
                event_number=event_number,
                player_id=player_id,
                session_id=session_id,
                timestamp=current_time,
                event_type=EventTypes.LEVEL_START,
                level_id=level_id,
            )
        )
        event_number += 1

        optional_events, event_number, current_time = _generate_optional_level_events(
            rng=rng,
            event_number=event_number,
            player_id=player_id,
            session_id=session_id,
            current_time=current_time,
            level_id=level_id,
        )
        events.extend(optional_events)

        current_time += timedelta(
            seconds=rng.randint(
                MIN_SECONDS_BEFORE_LEVEL_OUTCOME,
                MAX_SECONDS_BEFORE_LEVEL_OUTCOME,
            )
        )
        outcome = rng.choice(LEVEL_OUTCOMES)

        events.append(
            _build_event(
                event_number=event_number,
                player_id=player_id,
                session_id=session_id,
                timestamp=current_time,
                event_type=outcome,
                level_id=level_id,
                duration_seconds=rng.randint(
                    MIN_LEVEL_DURATION_SECONDS,
                    MAX_LEVEL_DURATION_SECONDS,
                ),
                result="success" if outcome == EventTypes.LEVEL_COMPLETE else "failure",
            )
        )
        event_number += 1

        if outcome == EventTypes.LEVEL_FAIL:
            break

    current_time += timedelta(
        seconds=rng.randint(
            MIN_SECONDS_BEFORE_SESSION_END,
            MAX_SECONDS_BEFORE_SESSION_END,
        )
    )
    session_duration = int((current_time - session_start).total_seconds())

    events.append(
        _build_event(
            event_number=event_number,
            player_id=player_id,
            session_id=session_id,
            timestamp=current_time,
            event_type=EventTypes.SESSION_END,
            duration_seconds=session_duration,
        )
    )
    event_number += 1

    return events, event_number


# ---------------------------------------------------------------------------
# _generate_optional_level_events
#
# Generates optional gameplay events that happen during a level attempt.
# ---------------------------------------------------------------------------
def _generate_optional_level_events(
    rng: random.Random,
    event_number: int,
    player_id: str,
    session_id: str,
    current_time: datetime,
    level_id: str,
) -> tuple[list[TelemetryEvent], int, datetime]:
    events: list[TelemetryEvent] = []

    optional_event_count = rng.randint(
        MIN_OPTIONAL_EVENTS_PER_LEVEL,
        MAX_OPTIONAL_EVENTS_PER_LEVEL,
    )

    for _ in range(optional_event_count):
        current_time += timedelta(
            seconds=rng.randint(
                MIN_SECONDS_BETWEEN_OPTIONAL_EVENTS,
                MAX_SECONDS_BETWEEN_OPTIONAL_EVENTS,
            )
        )
        event_type = rng.choice(OPTIONAL_EVENT_TYPES)

        event = _build_optional_event(
            rng=rng,
            event_number=event_number,
            player_id=player_id,
            session_id=session_id,
            timestamp=current_time,
            event_type=event_type,
            level_id=level_id,
        )

        events.append(event)
        event_number += 1

    return events, event_number, current_time


# ---------------------------------------------------------------------------
# _build_optional_event
#
# Builds one optional gameplay event with fields that match the event type.
# ---------------------------------------------------------------------------
def _build_optional_event(
    rng: random.Random,
    event_number: int,
    player_id: str,
    session_id: str,
    timestamp: datetime,
    event_type: str,
    level_id: str,
) -> TelemetryEvent:
    if event_type == EventTypes.ITEM_PICKUP:
        return _build_event(
            event_number=event_number,
            player_id=player_id,
            session_id=session_id,
            timestamp=timestamp,
            event_type=event_type,
            level_id=level_id,
            item_id=rng.choice(ITEM_IDS),
        )

    if event_type == EventTypes.ENEMY_DEFEATED:
        return _build_event(
            event_number=event_number,
            player_id=player_id,
            session_id=session_id,
            timestamp=timestamp,
            event_type=event_type,
            level_id=level_id,
            enemy_type=rng.choice(ENEMY_TYPES),
            damage_taken=rng.randint(
                MIN_ENEMY_DAMAGE_TAKEN,
                MAX_ENEMY_DAMAGE_TAKEN,
            ),
        )

    return _build_event(
        event_number=event_number,
        player_id=player_id,
        session_id=session_id,
        timestamp=timestamp,
        event_type=event_type,
        level_id=level_id,
        damage_taken=rng.randint(
            MIN_PLAYER_DEATH_DAMAGE_TAKEN,
            MAX_PLAYER_DEATH_DAMAGE_TAKEN,
        ),
        result="death",
    )


# ---------------------------------------------------------------------------
# _build_event
#
# Builds a TelemetryEvent with a consistent event ID and timestamp format.
# ---------------------------------------------------------------------------
def _build_event(
    event_number: int,
    player_id: str,
    session_id: str,
    timestamp: datetime,
    event_type: str,
    level_id: str | None = None,
    enemy_type: str | None = None,
    item_id: str | None = None,
    duration_seconds: int | None = None,
    damage_taken: int | None = None,
    result: str | None = None,
) -> TelemetryEvent:
    return TelemetryEvent(
        event_id=_format_id("event", event_number),
        player_id=player_id,
        session_id=session_id,
        timestamp=timestamp.isoformat(timespec="seconds"),
        event_type=event_type,
        level_id=level_id,
        enemy_type=enemy_type,
        item_id=item_id,
        duration_seconds=duration_seconds,
        damage_taken=damage_taken,
        result=result,
    )


# ---------------------------------------------------------------------------
# _format_id
#
# Formats deterministic IDs for players, levels, and events.
# ---------------------------------------------------------------------------
def _format_id(prefix: str, number: int) -> str:
    return f"{prefix}-{number:03d}"
