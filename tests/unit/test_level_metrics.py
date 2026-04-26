from __future__ import annotations

import pandas as pd
import pytest

from playtest_pulse.analytics.level_metrics import (
    calculate_level_attempts,
    calculate_level_outcomes,
    summarize_level_performance,
)
from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# _events_frame
#
# Builds a small telemetry DataFrame for level metric tests.
# ---------------------------------------------------------------------------
def _events_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_id": "event-001",
                "event_type": EventTypes.LEVEL_START,
                "level_id": "level-001",
            },
            {
                "event_id": "event-002",
                "event_type": EventTypes.LEVEL_COMPLETE,
                "level_id": "level-001",
            },
            {
                "event_id": "event-003",
                "event_type": EventTypes.LEVEL_START,
                "level_id": "level-001",
            },
            {
                "event_id": "event-004",
                "event_type": EventTypes.LEVEL_FAIL,
                "level_id": "level-001",
            },
            {
                "event_id": "event-005",
                "event_type": EventTypes.LEVEL_START,
                "level_id": "level-002",
            },
            {
                "event_id": "event-006",
                "event_type": EventTypes.LEVEL_COMPLETE,
                "level_id": "level-002",
            },
            {
                "event_id": "event-007",
                "event_type": EventTypes.ITEM_PICKUP,
                "level_id": "level-002",
            },
        ]
    )


# ---------------------------------------------------------------------------
# test_calculate_level_attempts_counts_level_start_events
#
# Verifies that level attempts count level_start events by level.
# ---------------------------------------------------------------------------
def test_calculate_level_attempts_counts_level_start_events() -> None:
    result = calculate_level_attempts(_events_frame())

    assert result.to_dict("records") == [
        {
            "level_id": "level-001",
            "attempt_count": 2,
        },
        {
            "level_id": "level-002",
            "attempt_count": 1,
        },
    ]


# ---------------------------------------------------------------------------
# test_calculate_level_outcomes_counts_completions_and_failures
#
# Verifies that level outcomes count complete and fail events by level.
# ---------------------------------------------------------------------------
def test_calculate_level_outcomes_counts_completions_and_failures() -> None:
    result = calculate_level_outcomes(_events_frame())

    assert result.to_dict("records") == [
        {
            "level_id": "level-001",
            "complete_count": 1,
            "fail_count": 1,
            "total_outcomes": 2,
            "completion_rate": 0.5,
            "failure_rate": 0.5,
        },
        {
            "level_id": "level-002",
            "complete_count": 1,
            "fail_count": 0,
            "total_outcomes": 1,
            "completion_rate": 1.0,
            "failure_rate": 0.0,
        },
    ]


# ---------------------------------------------------------------------------
# test_summarize_level_performance_combines_attempts_and_outcomes
#
# Verifies that level summary combines attempt and outcome metrics.
# ---------------------------------------------------------------------------
def test_summarize_level_performance_combines_attempts_and_outcomes() -> None:
    result = summarize_level_performance(_events_frame())

    assert result.to_dict("records") == [
        {
            "level_id": "level-001",
            "attempt_count": 2,
            "complete_count": 1,
            "fail_count": 1,
            "total_outcomes": 2,
            "completion_rate": 0.5,
            "failure_rate": 0.5,
        },
        {
            "level_id": "level-002",
            "attempt_count": 1,
            "complete_count": 1,
            "fail_count": 0,
            "total_outcomes": 1,
            "completion_rate": 1.0,
            "failure_rate": 0.0,
        },
    ]


# ---------------------------------------------------------------------------
# test_level_outcomes_returns_empty_frame_without_outcomes
#
# Verifies that outcome metrics return an empty shaped DataFrame without outcomes.
# ---------------------------------------------------------------------------
def test_level_outcomes_returns_empty_frame_without_outcomes() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.LEVEL_START,
                "level_id": "level-001",
            }
        ]
    )

    result = calculate_level_outcomes(events)

    assert result.empty
    assert list(result.columns) == [
        "level_id",
        "complete_count",
        "fail_count",
        "total_outcomes",
        "completion_rate",
        "failure_rate",
    ]


# ---------------------------------------------------------------------------
# test_level_summary_fills_missing_outcomes_with_zeroes
#
# Verifies that levels with attempts but no outcomes remain in the summary.
# ---------------------------------------------------------------------------
def test_level_summary_fills_missing_outcomes_with_zeroes() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.LEVEL_START,
                "level_id": "level-001",
            }
        ]
    )

    result = summarize_level_performance(events)

    assert result.to_dict("records") == [
        {
            "level_id": "level-001",
            "attempt_count": 1,
            "complete_count": 0,
            "fail_count": 0,
            "total_outcomes": 0,
            "completion_rate": 0.0,
            "failure_rate": 0.0,
        }
    ]


# ---------------------------------------------------------------------------
# test_level_metrics_ignore_rows_without_level_id
#
# Verifies that rows without level_id do not appear in level metrics.
# ---------------------------------------------------------------------------
def test_level_metrics_ignore_rows_without_level_id() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.LEVEL_START,
                "level_id": None,
            }
        ]
    )

    result = calculate_level_attempts(events)

    assert result.empty


# ---------------------------------------------------------------------------
# test_level_metrics_reject_missing_required_columns
#
# Verifies that metrics fail clearly when required DataFrame columns are absent.
# ---------------------------------------------------------------------------
def test_level_metrics_reject_missing_required_columns() -> None:
    events = pd.DataFrame([{"event_type": EventTypes.LEVEL_START}])

    with pytest.raises(ValueError, match="level_id"):
        calculate_level_attempts(events)
