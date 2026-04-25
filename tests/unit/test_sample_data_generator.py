from __future__ import annotations

from playtest_pulse.config import GenerationConfig, ProjectConfig
from playtest_pulse.domain import EventTypes, TelemetryEvent
from playtest_pulse.ingestion import generate_sample_events


# ---------------------------------------------------------------------------
# _project_config
#
# Builds project settings for deterministic sample data generation tests.
# ---------------------------------------------------------------------------
def _project_config(seed: int = 42) -> ProjectConfig:
    return ProjectConfig(
        name="playtest-pulse",
        version="0.1.0",
        seed=seed,
    )


# ---------------------------------------------------------------------------
# _generation_config
#
# Builds generation settings for small and fast sample data tests.
# ---------------------------------------------------------------------------
def _generation_config() -> GenerationConfig:
    return GenerationConfig(
        player_count=5,
        min_sessions_per_player=1,
        max_sessions_per_player=2,
        level_count=3,
    )


# ---------------------------------------------------------------------------
# test_generate_sample_events_returns_events
#
# Verifies that sample generation returns telemetry event objects.
# ---------------------------------------------------------------------------
def test_generate_sample_events_returns_events() -> None:
    events = generate_sample_events(
        project_config=_project_config(),
        generation_config=_generation_config(),
    )

    assert events
    assert all(isinstance(event, TelemetryEvent) for event in events)


# ---------------------------------------------------------------------------
# test_generate_sample_events_is_deterministic
#
# Verifies that the same seed and config produce the same event sequence.
# ---------------------------------------------------------------------------
def test_generate_sample_events_is_deterministic() -> None:
    first_events = generate_sample_events(
        project_config=_project_config(seed=123),
        generation_config=_generation_config(),
    )
    second_events = generate_sample_events(
        project_config=_project_config(seed=123),
        generation_config=_generation_config(),
    )

    assert first_events == second_events


# ---------------------------------------------------------------------------
# test_generate_sample_events_changes_with_different_seed
#
# Verifies that different seeds can produce different event sequences.
# ---------------------------------------------------------------------------
def test_generate_sample_events_changes_with_different_seed() -> None:
    first_events = generate_sample_events(
        project_config=_project_config(seed=123),
        generation_config=_generation_config(),
    )
    second_events = generate_sample_events(
        project_config=_project_config(seed=456),
        generation_config=_generation_config(),
    )

    assert first_events != second_events


# ---------------------------------------------------------------------------
# test_generate_sample_events_includes_session_boundaries
#
# Verifies that generated data includes session start and end events.
# ---------------------------------------------------------------------------
def test_generate_sample_events_includes_session_boundaries() -> None:
    events = generate_sample_events(
        project_config=_project_config(),
        generation_config=_generation_config(),
    )
    event_types = {event.event_type for event in events}

    assert EventTypes.SESSION_START in event_types
    assert EventTypes.SESSION_END in event_types


# ---------------------------------------------------------------------------
# test_generate_sample_events_includes_level_events
#
# Verifies that generated data includes level starts and level outcomes.
# ---------------------------------------------------------------------------
def test_generate_sample_events_includes_level_events() -> None:
    events = generate_sample_events(
        project_config=_project_config(),
        generation_config=_generation_config(),
    )
    event_types = {event.event_type for event in events}

    assert EventTypes.LEVEL_START in event_types
    assert event_types.intersection(
        {
            EventTypes.LEVEL_COMPLETE,
            EventTypes.LEVEL_FAIL,
        }
    )


# ---------------------------------------------------------------------------
# test_generate_sample_events_uses_unique_event_ids
#
# Verifies that each generated event has a unique event ID.
# ---------------------------------------------------------------------------
def test_generate_sample_events_uses_unique_event_ids() -> None:
    events = generate_sample_events(
        project_config=_project_config(),
        generation_config=_generation_config(),
    )

    event_ids = [event.event_id for event in events]

    assert len(event_ids) == len(set(event_ids))


# ---------------------------------------------------------------------------
# test_generate_sample_events_respects_player_count
#
# Verifies that generated data contains the configured number of players.
# ---------------------------------------------------------------------------
def test_generate_sample_events_respects_player_count() -> None:
    events = generate_sample_events(
        project_config=_project_config(),
        generation_config=_generation_config(),
    )

    player_ids = {event.player_id for event in events}

    assert len(player_ids) == _generation_config().player_count


# ---------------------------------------------------------------------------
# test_generate_sample_events_respects_session_range
#
# Verifies that generated session counts stay inside the configured range.
# ---------------------------------------------------------------------------
def test_generate_sample_events_respects_session_range() -> None:
    config = _generation_config()
    events = generate_sample_events(
        project_config=_project_config(),
        generation_config=config,
    )

    session_ids_by_player: dict[str, set[str]] = {}

    for event in events:
        session_ids_by_player.setdefault(event.player_id, set()).add(event.session_id)

    for session_ids in session_ids_by_player.values():
        assert config.min_sessions_per_player <= len(session_ids)
        assert len(session_ids) <= config.max_sessions_per_player
