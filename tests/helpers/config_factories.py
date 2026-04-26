from __future__ import annotations

from pathlib import Path

from playtest_pulse.config import (
    AppConfig,
    DashboardConfig,
    DataConfig,
    GenerationConfig,
    ProjectConfig,
)


# ---------------------------------------------------------------------------
# make_project_config
#
# Builds project settings for tests.
# ---------------------------------------------------------------------------
def make_project_config(seed: int = 42) -> ProjectConfig:
    return ProjectConfig(
        name="playtest-pulse",
        version="0.1.0",
        seed=seed,
    )


# ---------------------------------------------------------------------------
# make_generation_config
#
# Builds generation settings for small test datasets.
# ---------------------------------------------------------------------------
def make_generation_config(
    player_count: int = 5,
    min_sessions_per_player: int = 1,
    max_sessions_per_player: int = 2,
    level_count: int = 3,
) -> GenerationConfig:
    return GenerationConfig(
        player_count=player_count,
        min_sessions_per_player=min_sessions_per_player,
        max_sessions_per_player=max_sessions_per_player,
        level_count=level_count,
    )


# ---------------------------------------------------------------------------
# make_app_config
#
# Builds application settings for tests using temporary file paths.
# ---------------------------------------------------------------------------
def make_app_config(
    tmp_path: Path,
    raw_events_filename: str = "sample_events.csv",
    database_filename: str = "telemetry.sqlite3",
) -> AppConfig:
    return AppConfig(
        project=make_project_config(),
        data=DataConfig(
            raw_events_path=str(tmp_path / raw_events_filename),
            processed_database_path=str(tmp_path / database_filename),
        ),
        generation=make_generation_config(),
        dashboard=DashboardConfig(
            title="Playtest Pulse",
        ),
    )
