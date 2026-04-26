from __future__ import annotations

import pandas as pd
import pytest

from playtest_pulse.analytics.item_metrics import (
    calculate_item_pickups,
    count_total_item_pickups,
    get_most_picked_up_item,
)
from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# _events_frame
#
# Builds a small telemetry DataFrame for item metric tests.
# ---------------------------------------------------------------------------
def _events_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "item_id": "health_potion",
            },
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "item_id": "health_potion",
            },
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "item_id": "iron_key",
            },
            {
                "event_type": EventTypes.ENEMY_DEFEATED,
                "item_id": None,
            },
        ]
    )


# ---------------------------------------------------------------------------
# test_calculate_item_pickups_counts_pickups_by_item
#
# Verifies that item pickups are counted by item ID.
# ---------------------------------------------------------------------------
def test_calculate_item_pickups_counts_pickups_by_item() -> None:
    result = calculate_item_pickups(_events_frame())

    assert result.to_dict("records") == [
        {
            "item_id": "health_potion",
            "pickup_count": 2,
        },
        {
            "item_id": "iron_key",
            "pickup_count": 1,
        },
    ]


# ---------------------------------------------------------------------------
# test_count_total_item_pickups_counts_all_pickup_events
#
# Verifies that total pickups counts all item_pickup events.
# ---------------------------------------------------------------------------
def test_count_total_item_pickups_counts_all_pickup_events() -> None:
    assert count_total_item_pickups(_events_frame()) == 3


# ---------------------------------------------------------------------------
# test_get_most_picked_up_item_returns_highest_count_item
#
# Verifies that the most picked up item is selected by pickup count.
# ---------------------------------------------------------------------------
def test_get_most_picked_up_item_returns_highest_count_item() -> None:
    assert get_most_picked_up_item(_events_frame()) == "health_potion"


# ---------------------------------------------------------------------------
# test_get_most_picked_up_item_breaks_ties_by_item_id
#
# Verifies that ties are resolved by item ID for deterministic output.
# ---------------------------------------------------------------------------
def test_get_most_picked_up_item_breaks_ties_by_item_id() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "item_id": "iron_key",
            },
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "item_id": "health_potion",
            },
        ]
    )

    assert get_most_picked_up_item(events) == "health_potion"


# ---------------------------------------------------------------------------
# test_item_metrics_return_empty_or_none_without_pickups
#
# Verifies that item metrics handle data with no item pickup events.
# ---------------------------------------------------------------------------
def test_item_metrics_return_empty_or_none_without_pickups() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.ENEMY_DEFEATED,
                "item_id": None,
            }
        ]
    )

    assert calculate_item_pickups(events).empty
    assert count_total_item_pickups(events) == 0
    assert get_most_picked_up_item(events) is None


# ---------------------------------------------------------------------------
# test_item_metrics_ignore_pickups_without_item_id
#
# Verifies that pickup rows without item IDs are ignored in item count tables.
# ---------------------------------------------------------------------------
def test_item_metrics_ignore_pickups_without_item_id() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "item_id": None,
            }
        ]
    )

    assert calculate_item_pickups(events).empty


# ---------------------------------------------------------------------------
# test_item_metrics_reject_missing_required_columns
#
# Verifies that item metrics fail clearly when required columns are absent.
# ---------------------------------------------------------------------------
def test_item_metrics_reject_missing_required_columns() -> None:
    events = pd.DataFrame([{"event_type": EventTypes.ITEM_PICKUP}])

    with pytest.raises(ValueError, match="item_id"):
        calculate_item_pickups(events)
