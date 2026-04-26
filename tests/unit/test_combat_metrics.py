from __future__ import annotations

import pandas as pd
import pytest

from playtest_pulse.analytics.combat_metrics import (
    calculate_average_damage_taken_by_level,
    calculate_deaths_by_level,
    calculate_enemy_defeats,
    summarize_combat,
)
from playtest_pulse.domain import EventTypes


# ---------------------------------------------------------------------------
# _events_frame
#
# Builds a small telemetry DataFrame for combat metric tests.
# ---------------------------------------------------------------------------
def _events_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_type": EventTypes.PLAYER_DEATH,
                "level_id": "level-001",
                "enemy_type": None,
                "damage_taken": 20,
            },
            {
                "event_type": EventTypes.PLAYER_DEATH,
                "level_id": "level-001",
                "enemy_type": None,
                "damage_taken": 15,
            },
            {
                "event_type": EventTypes.PLAYER_DEATH,
                "level_id": "level-002",
                "enemy_type": None,
                "damage_taken": 10,
            },
            {
                "event_type": EventTypes.ENEMY_DEFEATED,
                "level_id": "level-001",
                "enemy_type": "slime",
                "damage_taken": 5,
            },
            {
                "event_type": EventTypes.ENEMY_DEFEATED,
                "level_id": "level-002",
                "enemy_type": "goblin",
                "damage_taken": 8,
            },
            {
                "event_type": EventTypes.ENEMY_DEFEATED,
                "level_id": "level-002",
                "enemy_type": "goblin",
                "damage_taken": 6,
            },
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "level_id": "level-001",
                "enemy_type": None,
                "damage_taken": None,
            },
        ]
    )


# ---------------------------------------------------------------------------
# test_calculate_deaths_by_level_counts_player_deaths
#
# Verifies that player deaths are counted by level.
# ---------------------------------------------------------------------------
def test_calculate_deaths_by_level_counts_player_deaths() -> None:
    result = calculate_deaths_by_level(_events_frame())

    assert result.to_dict("records") == [
        {
            "level_id": "level-001",
            "death_count": 2,
        },
        {
            "level_id": "level-002",
            "death_count": 1,
        },
    ]


# ---------------------------------------------------------------------------
# test_calculate_enemy_defeats_counts_defeats_by_enemy_type
#
# Verifies that enemy defeats are counted by enemy type.
# ---------------------------------------------------------------------------
def test_calculate_enemy_defeats_counts_defeats_by_enemy_type() -> None:
    result = calculate_enemy_defeats(_events_frame())

    assert result.to_dict("records") == [
        {
            "enemy_type": "goblin",
            "defeat_count": 2,
        },
        {
            "enemy_type": "slime",
            "defeat_count": 1,
        },
    ]


# ---------------------------------------------------------------------------
# test_calculate_average_damage_taken_by_level_returns_average_damage
#
# Verifies that combat damage is averaged by level.
# ---------------------------------------------------------------------------
def test_calculate_average_damage_taken_by_level_returns_average_damage() -> None:
    result = calculate_average_damage_taken_by_level(_events_frame())

    assert result.to_dict("records") == [
        {
            "level_id": "level-001",
            "average_damage_taken": pytest.approx(13.3333333333),
        },
        {
            "level_id": "level-002",
            "average_damage_taken": 8.0,
        },
    ]


# ---------------------------------------------------------------------------
# test_summarize_combat_returns_expected_totals
#
# Verifies that combat summary returns total death and defeat counts.
# ---------------------------------------------------------------------------
def test_summarize_combat_returns_expected_totals() -> None:
    assert summarize_combat(_events_frame()) == {
        "player_deaths": 3,
        "enemy_defeats": 3,
    }


# ---------------------------------------------------------------------------
# test_combat_metrics_return_empty_frames_without_matching_events
#
# Verifies that combat metric tables keep their shape when no events match.
# ---------------------------------------------------------------------------
def test_combat_metrics_return_empty_frames_without_matching_events() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.ITEM_PICKUP,
                "level_id": "level-001",
                "enemy_type": None,
                "damage_taken": None,
            }
        ]
    )

    assert calculate_deaths_by_level(events).empty
    assert calculate_enemy_defeats(events).empty
    assert calculate_average_damage_taken_by_level(events).empty


# ---------------------------------------------------------------------------
# test_combat_metrics_ignore_rows_missing_group_values
#
# Verifies that combat metrics ignore rows without required grouping values.
# ---------------------------------------------------------------------------
def test_combat_metrics_ignore_rows_missing_group_values() -> None:
    events = pd.DataFrame(
        [
            {
                "event_type": EventTypes.PLAYER_DEATH,
                "level_id": None,
                "enemy_type": None,
                "damage_taken": 10,
            },
            {
                "event_type": EventTypes.ENEMY_DEFEATED,
                "level_id": "level-001",
                "enemy_type": None,
                "damage_taken": 3,
            },
        ]
    )

    assert calculate_deaths_by_level(events).empty
    assert calculate_enemy_defeats(events).empty


# ---------------------------------------------------------------------------
# test_combat_metrics_reject_missing_required_columns
#
# Verifies that combat metrics fail clearly when required columns are absent.
# ---------------------------------------------------------------------------
def test_combat_metrics_reject_missing_required_columns() -> None:
    events = pd.DataFrame([{"event_type": EventTypes.PLAYER_DEATH}])

    with pytest.raises(ValueError, match="level_id"):
        calculate_deaths_by_level(events)
