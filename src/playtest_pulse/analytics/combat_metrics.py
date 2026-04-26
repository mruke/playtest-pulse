from __future__ import annotations

import pandas as pd

from playtest_pulse.analytics.frame_validation import require_columns
from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# calculate_deaths_by_level
#
# Counts player death events by level.
# ---------------------------------------------------------------------------
def calculate_deaths_by_level(events: pd.DataFrame) -> pd.DataFrame:
    require_columns(events, ["event_type", "level_id"])

    deaths = events[events["event_type"] == EventTypes.PLAYER_DEATH]
    deaths = deaths.dropna(subset=["level_id"])

    if deaths.empty:
        return pd.DataFrame(columns=["level_id", "death_count"])

    return (
        deaths.groupby("level_id")
        .size()
        .reset_index(name="death_count")
        .sort_values("level_id", ignore_index=True)
    )


# ---------------------------------------------------------------------------
# calculate_enemy_defeats
#
# Counts enemy defeated events by enemy type.
# ---------------------------------------------------------------------------
def calculate_enemy_defeats(events: pd.DataFrame) -> pd.DataFrame:
    require_columns(events, ["event_type", "enemy_type"])

    defeats = events[events["event_type"] == EventTypes.ENEMY_DEFEATED]
    defeats = defeats.dropna(subset=["enemy_type"])

    if defeats.empty:
        return pd.DataFrame(columns=["enemy_type", "defeat_count"])

    return (
        defeats.groupby("enemy_type")
        .size()
        .reset_index(name="defeat_count")
        .sort_values("enemy_type", ignore_index=True)
    )


# ---------------------------------------------------------------------------
# calculate_average_damage_taken_by_level
#
# Calculates average damage taken by level from combat-related events.
# ---------------------------------------------------------------------------
def calculate_average_damage_taken_by_level(events: pd.DataFrame) -> pd.DataFrame:
    require_columns(events, ["event_type", "level_id", "damage_taken"])

    combat_events = events[
        events["event_type"].isin(
            [
                EventTypes.PLAYER_DEATH,
                EventTypes.ENEMY_DEFEATED,
            ]
        )
    ]
    combat_events = combat_events.dropna(subset=["level_id", "damage_taken"])

    if combat_events.empty:
        return pd.DataFrame(columns=["level_id", "average_damage_taken"])

    return (
        combat_events.groupby("level_id")["damage_taken"]
        .mean()
        .reset_index(name="average_damage_taken")
        .sort_values("level_id", ignore_index=True)
    )


# ---------------------------------------------------------------------------
# summarize_combat
#
# Builds a compact summary of combat metrics.
# ---------------------------------------------------------------------------
def summarize_combat(events: pd.DataFrame) -> dict[str, int]:
    require_columns(events, ["event_type"])

    death_count = int((events["event_type"] == EventTypes.PLAYER_DEATH).sum())
    enemy_defeat_count = int((events["event_type"] == EventTypes.ENEMY_DEFEATED).sum())

    return {
        "player_deaths": death_count,
        "enemy_defeats": enemy_defeat_count,
    }
