from __future__ import annotations

import pandas as pd

from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# calculate_level_attempts
#
# Counts level_start events by level.
# ---------------------------------------------------------------------------
def calculate_level_attempts(events: pd.DataFrame) -> pd.DataFrame:
    _require_columns(events, ["event_type", "level_id"])

    level_starts = events[events["event_type"] == EventTypes.LEVEL_START]
    level_starts = level_starts.dropna(subset=["level_id"])

    return _count_by_level(
        level_starts,
        count_column_name="attempt_count",
    )


# ---------------------------------------------------------------------------
# calculate_level_outcomes
#
# Counts level completion and failure events by level.
# ---------------------------------------------------------------------------
def calculate_level_outcomes(events: pd.DataFrame) -> pd.DataFrame:
    _require_columns(events, ["event_type", "level_id"])

    level_outcomes = events[
        events["event_type"].isin(
            [
                EventTypes.LEVEL_COMPLETE,
                EventTypes.LEVEL_FAIL,
            ]
        )
    ]
    level_outcomes = level_outcomes.dropna(subset=["level_id"])

    if level_outcomes.empty:
        return pd.DataFrame(
            columns=[
                "level_id",
                "complete_count",
                "fail_count",
                "total_outcomes",
                "completion_rate",
                "failure_rate",
            ]
        )

    outcome_counts = (
        level_outcomes.groupby(["level_id", "event_type"])
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    if EventTypes.LEVEL_COMPLETE not in outcome_counts.columns:
        outcome_counts[EventTypes.LEVEL_COMPLETE] = 0

    if EventTypes.LEVEL_FAIL not in outcome_counts.columns:
        outcome_counts[EventTypes.LEVEL_FAIL] = 0

    result = outcome_counts.rename(
        columns={
            EventTypes.LEVEL_COMPLETE: "complete_count",
            EventTypes.LEVEL_FAIL: "fail_count",
        }
    )

    result["total_outcomes"] = result["complete_count"] + result["fail_count"]
    result["completion_rate"] = result["complete_count"] / result["total_outcomes"]
    result["failure_rate"] = result["fail_count"] / result["total_outcomes"]

    return result[
        [
            "level_id",
            "complete_count",
            "fail_count",
            "total_outcomes",
            "completion_rate",
            "failure_rate",
        ]
    ].sort_values("level_id", ignore_index=True)


# ---------------------------------------------------------------------------
# summarize_level_performance
#
# Combines level attempts and outcomes into one level performance table.
# ---------------------------------------------------------------------------
def summarize_level_performance(events: pd.DataFrame) -> pd.DataFrame:
    attempts = calculate_level_attempts(events)
    outcomes = calculate_level_outcomes(events)

    if attempts.empty:
        return pd.DataFrame(
            columns=[
                "level_id",
                "attempt_count",
                "complete_count",
                "fail_count",
                "total_outcomes",
                "completion_rate",
                "failure_rate",
            ]
        )

    summary = attempts.merge(
        outcomes,
        on="level_id",
        how="left",
    )

    fill_values = {
        "complete_count": 0,
        "fail_count": 0,
        "total_outcomes": 0,
        "completion_rate": 0.0,
        "failure_rate": 0.0,
    }
    summary = summary.fillna(fill_values)

    integer_columns = [
        "attempt_count",
        "complete_count",
        "fail_count",
        "total_outcomes",
    ]
    summary[integer_columns] = summary[integer_columns].astype(int)

    return summary[
        [
            "level_id",
            "attempt_count",
            "complete_count",
            "fail_count",
            "total_outcomes",
            "completion_rate",
            "failure_rate",
        ]
    ].sort_values("level_id", ignore_index=True)


# ---------------------------------------------------------------------------
# _count_by_level
#
# Counts rows by level_id and returns a consistently shaped DataFrame.
# ---------------------------------------------------------------------------
def _count_by_level(
    events: pd.DataFrame,
    count_column_name: str,
) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame(columns=["level_id", count_column_name])

    return (
        events.groupby("level_id")
        .size()
        .reset_index(name=count_column_name)
        .sort_values("level_id", ignore_index=True)
    )


# ---------------------------------------------------------------------------
# _require_columns
#
# Verifies that the DataFrame contains the columns needed by a metric.
# ---------------------------------------------------------------------------
def _require_columns(events: pd.DataFrame, columns: list[str]) -> None:
    missing_columns = [column for column in columns if column not in events.columns]

    if missing_columns:
        joined_columns = ", ".join(missing_columns)
        raise ValueError(f"events DataFrame is missing columns: {joined_columns}")
