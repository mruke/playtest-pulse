from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from playtest_pulse.config import load_config
from playtest_pulse.dashboard import DashboardData, load_dashboard_data


# ---------------------------------------------------------------------------
# render_dashboard
#
# Loads dashboard data from config and renders the Streamlit dashboard.
# ---------------------------------------------------------------------------
def render_dashboard(config_path: str | Path) -> None:
    config = load_config(config_path)

    st.set_page_config(
        page_title=config.dashboard.title,
        layout="wide",
    )
    st.title(config.dashboard.title)
    st.caption("Simulated game playtest telemetry analytics.")

    try:
        dashboard_data = load_dashboard_data(config)
    except FileNotFoundError as error:
        st.error(str(error))
        st.info(
            "Run `python scripts/generate_sample_data.py` and "
            "`python scripts/ingest_events.py --replace` before opening the dashboard."
        )
        return

    _render_summary_metrics(dashboard_data)
    _render_level_section(dashboard_data)
    _render_combat_section(dashboard_data)
    _render_item_section(dashboard_data)
    _render_raw_events_section(dashboard_data)


# ---------------------------------------------------------------------------
# _render_summary_metrics
#
# Renders top-level player, session, combat, and item summary metrics.
# ---------------------------------------------------------------------------
def _render_summary_metrics(dashboard_data: DashboardData) -> None:
    session_summary = dashboard_data.session_summary
    combat_summary = dashboard_data.combat_summary

    st.header("Overview")

    columns = st.columns(5)
    columns[0].metric("Players", session_summary["total_players"])
    columns[1].metric("Sessions", session_summary["total_sessions"])
    columns[2].metric("Returning Players", session_summary["returning_players"])
    columns[3].metric("Player Deaths", combat_summary["player_deaths"])
    columns[4].metric(
        "Most Picked Item",
        dashboard_data.most_picked_up_item or "None",
    )

    st.metric(
        "Average Session Duration",
        f"{session_summary['average_session_duration_seconds']:.1f} seconds",
    )


# ---------------------------------------------------------------------------
# _render_level_section
#
# Renders level attempts, outcomes, and completion metrics.
# ---------------------------------------------------------------------------
def _render_level_section(dashboard_data: DashboardData) -> None:
    st.header("Level Performance")

    level_performance = dashboard_data.level_performance

    if level_performance.empty:
        st.info("No level performance data available.")
        return

    st.dataframe(level_performance, width="stretch")

    chart_data = level_performance.set_index("level_id")[
        [
            "completion_rate",
            "failure_rate",
        ]
    ]
    st.bar_chart(chart_data)


# ---------------------------------------------------------------------------
# _render_combat_section
#
# Renders combat-related telemetry metrics.
# ---------------------------------------------------------------------------
def _render_combat_section(dashboard_data: DashboardData) -> None:
    st.header("Combat")

    left_column, right_column = st.columns(2)

    with left_column:
        st.subheader("Deaths by Level")
        _render_table_or_info(
            dashboard_data.deaths_by_level,
            "No player death events available.",
        )

        if not dashboard_data.deaths_by_level.empty:
            st.bar_chart(
                dashboard_data.deaths_by_level.set_index("level_id")["death_count"]
            )

    with right_column:
        st.subheader("Enemy Defeats")
        _render_table_or_info(
            dashboard_data.enemy_defeats,
            "No enemy defeat events available.",
        )

        if not dashboard_data.enemy_defeats.empty:
            st.bar_chart(
                dashboard_data.enemy_defeats.set_index("enemy_type")["defeat_count"]
            )

    st.subheader("Average Damage Taken by Level")
    _render_table_or_info(
        dashboard_data.average_damage_by_level,
        "No damage data available.",
    )

    if not dashboard_data.average_damage_by_level.empty:
        st.bar_chart(
            dashboard_data.average_damage_by_level.set_index("level_id")[
                "average_damage_taken"
            ]
        )


# ---------------------------------------------------------------------------
# _render_item_section
#
# Renders item pickup metrics.
# ---------------------------------------------------------------------------
def _render_item_section(dashboard_data: DashboardData) -> None:
    st.header("Items")

    _render_table_or_info(
        dashboard_data.item_pickups,
        "No item pickup events available.",
    )

    if not dashboard_data.item_pickups.empty:
        st.bar_chart(dashboard_data.item_pickups.set_index("item_id")["pickup_count"])


# ---------------------------------------------------------------------------
# _render_raw_events_section
#
# Renders the raw validated telemetry events used by the dashboard.
# ---------------------------------------------------------------------------
def _render_raw_events_section(dashboard_data: DashboardData) -> None:
    with st.expander("Raw Events"):
        st.dataframe(
            dashboard_data.raw_events,
            width="stretch",
        )


# ---------------------------------------------------------------------------
# _render_table_or_info
#
# Renders a DataFrame or an informational message when the DataFrame is empty.
# ---------------------------------------------------------------------------
def _render_table_or_info(frame: pd.DataFrame, empty_message: str) -> None:
    if frame.empty:
        st.info(empty_message)
        return

    st.dataframe(frame, width="stretch")
