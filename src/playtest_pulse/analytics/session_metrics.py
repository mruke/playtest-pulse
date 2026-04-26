from __future__ import annotations

import pandas as pd

from playtest_pulse.analytics.frame_validation import require_columns
from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# count_total_sessions
#
# Counts the number of unique sessions in the telemetry event data.
# ---------------------------------------------------------------------------
def count_total_sessions(events: pd.DataFrame) -> int:
    require_columns(events, ["session_id"])

    return int(events["session_id"].nunique())


# ---------------------------------------------------------------------------
# count_total_players
#
# Counts the number of unique players in the telemetry event data.
# ---------------------------------------------------------------------------
def count_total_players(events: pd.DataFrame) -> int:
    require_columns(events, ["player_id"])

    return int(events["player_id"].nunique())


# ---------------------------------------------------------------------------
# calculate_average_session_duration
#
# Calculates the average duration from session_end events.
# ---------------------------------------------------------------------------
def calculate_average_session_duration(events: pd.DataFrame) -> float:
    require_columns(events, ["event_type", "duration_seconds"])

    session_end_events = events[events["event_type"] == EventTypes.SESSION_END]

    if session_end_events.empty:
        raise ValueError("events must contain at least one session_end event.")

    durations = session_end_events["duration_seconds"].dropna()

    if durations.empty:
        raise ValueError("session_end events must include duration_seconds.")

    return float(durations.mean())


# ---------------------------------------------------------------------------
# count_returning_players
#
# Counts players who have more than one session.
# ---------------------------------------------------------------------------
def count_returning_players(events: pd.DataFrame) -> int:
    require_columns(events, ["player_id", "session_id"])

    sessions_by_player = events.groupby("player_id")["session_id"].nunique()
    returning_players = sessions_by_player[sessions_by_player > 1]

    return int(returning_players.count())


# ---------------------------------------------------------------------------
# summarize_sessions
#
# Builds a compact summary of player and session activity.
# ---------------------------------------------------------------------------
def summarize_sessions(events: pd.DataFrame) -> dict[str, int | float]:
    return {
        "total_players": count_total_players(events),
        "total_sessions": count_total_sessions(events),
        "returning_players": count_returning_players(events),
        "average_session_duration_seconds": calculate_average_session_duration(events),
    }
