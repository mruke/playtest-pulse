from __future__ import annotations

import pandas as pd
import pytest

from playtest_pulse.analytics.session_metrics import (
    calculate_average_session_duration,
    count_returning_players,
    count_total_players,
    count_total_sessions,
    summarize_sessions,
)
from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# _events_frame
#
# Builds a small telemetry DataFrame for session metric tests.
# ---------------------------------------------------------------------------
def _events_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_id": "event-001",
                "player_id": "player-001",
                "session_id": "session-001",
                "event_type": EventTypes.SESSION_START,
                "duration_seconds": None,
            },
            {
                "event_id": "event-002",
                "player_id": "player-001",
                "session_id": "session-001",
                "event_type": EventTypes.SESSION_END,
                "duration_seconds": 120,
            },
            {
                "event_id": "event-003",
                "player_id": "player-001",
                "session_id": "session-002",
                "event_type": EventTypes.SESSION_START,
                "duration_seconds": None,
            },
            {
                "event_id": "event-004",
                "player_id": "player-001",
                "session_id": "session-002",
                "event_type": EventTypes.SESSION_END,
                "duration_seconds": 180,
            },
            {
                "event_id": "event-005",
                "player_id": "player-002",
                "session_id": "session-003",
                "event_type": EventTypes.SESSION_START,
                "duration_seconds": None,
            },
            {
                "event_id": "event-006",
                "player_id": "player-002",
                "session_id": "session-003",
                "event_type": EventTypes.SESSION_END,
                "duration_seconds": 60,
            },
        ]
    )


# ---------------------------------------------------------------------------
# test_count_total_sessions_returns_unique_session_count
#
# Verifies that total sessions count unique session IDs.
# ---------------------------------------------------------------------------
def test_count_total_sessions_returns_unique_session_count() -> None:
    assert count_total_sessions(_events_frame()) == 3


# ---------------------------------------------------------------------------
# test_count_total_players_returns_unique_player_count
#
# Verifies that total players count unique player IDs.
# ---------------------------------------------------------------------------
def test_count_total_players_returns_unique_player_count() -> None:
    assert count_total_players(_events_frame()) == 2


# ---------------------------------------------------------------------------
# test_calculate_average_session_duration_returns_average_end_duration
#
# Verifies that average session duration uses session_end events.
# ---------------------------------------------------------------------------
def test_calculate_average_session_duration_returns_average_end_duration() -> None:
    assert calculate_average_session_duration(_events_frame()) == 120.0


# ---------------------------------------------------------------------------
# test_count_returning_players_counts_players_with_multiple_sessions
#
# Verifies that returning players have more than one unique session.
# ---------------------------------------------------------------------------
def test_count_returning_players_counts_players_with_multiple_sessions() -> None:
    assert count_returning_players(_events_frame()) == 1


# ---------------------------------------------------------------------------
# test_summarize_sessions_returns_expected_summary
#
# Verifies that the session summary includes the expected metric values.
# ---------------------------------------------------------------------------
def test_summarize_sessions_returns_expected_summary() -> None:
    summary = summarize_sessions(_events_frame())

    assert summary == {
        "total_players": 2,
        "total_sessions": 3,
        "returning_players": 1,
        "average_session_duration_seconds": 120.0,
    }


# ---------------------------------------------------------------------------
# test_average_session_duration_rejects_missing_session_end_events
#
# Verifies that average duration requires at least one session_end event.
# ---------------------------------------------------------------------------
def test_average_session_duration_rejects_missing_session_end_events() -> None:
    events = pd.DataFrame(
        [
            {
                "player_id": "player-001",
                "session_id": "session-001",
                "event_type": EventTypes.SESSION_START,
                "duration_seconds": None,
            }
        ]
    )

    with pytest.raises(ValueError, match="session_end"):
        calculate_average_session_duration(events)


# ---------------------------------------------------------------------------
# test_average_session_duration_rejects_missing_durations
#
# Verifies that session_end events must include duration values.
# ---------------------------------------------------------------------------
def test_average_session_duration_rejects_missing_durations() -> None:
    events = pd.DataFrame(
        [
            {
                "player_id": "player-001",
                "session_id": "session-001",
                "event_type": EventTypes.SESSION_END,
                "duration_seconds": None,
            }
        ]
    )

    with pytest.raises(ValueError, match="duration_seconds"):
        calculate_average_session_duration(events)


# ---------------------------------------------------------------------------
# test_session_metrics_reject_missing_required_columns
#
# Verifies that metrics fail clearly when required DataFrame columns are absent.
# ---------------------------------------------------------------------------
def test_session_metrics_reject_missing_required_columns() -> None:
    events = pd.DataFrame([{"player_id": "player-001"}])

    with pytest.raises(ValueError, match="session_id"):
        count_total_sessions(events)
