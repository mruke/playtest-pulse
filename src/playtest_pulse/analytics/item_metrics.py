from __future__ import annotations

import pandas as pd

from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# calculate_item_pickups
#
# Counts item pickup events by item ID.
# ---------------------------------------------------------------------------
def calculate_item_pickups(events: pd.DataFrame) -> pd.DataFrame:
    _require_columns(events, ["event_type", "item_id"])

    pickups = events[events["event_type"] == EventTypes.ITEM_PICKUP]
    pickups = pickups.dropna(subset=["item_id"])

    if pickups.empty:
        return pd.DataFrame(columns=["item_id", "pickup_count"])

    return (
        pickups.groupby("item_id")
        .size()
        .reset_index(name="pickup_count")
        .sort_values("item_id", ignore_index=True)
    )


# ---------------------------------------------------------------------------
# count_total_item_pickups
#
# Counts all item pickup events.
# ---------------------------------------------------------------------------
def count_total_item_pickups(events: pd.DataFrame) -> int:
    _require_columns(events, ["event_type"])

    return int((events["event_type"] == EventTypes.ITEM_PICKUP).sum())


# ---------------------------------------------------------------------------
# get_most_picked_up_item
#
# Returns the item ID with the highest pickup count.
# ---------------------------------------------------------------------------
def get_most_picked_up_item(events: pd.DataFrame) -> str | None:
    pickups = calculate_item_pickups(events)

    if pickups.empty:
        return None

    most_common_row = pickups.sort_values(
        ["pickup_count", "item_id"],
        ascending=[False, True],
        ignore_index=True,
    ).iloc[0]

    return str(most_common_row["item_id"])


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
