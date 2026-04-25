from __future__ import annotations

from dataclasses import dataclass


# ---------------------------------------------------------------------------
# ProjectConfig
#
# Stores project-level metadata and reproducibility settings.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ProjectConfig:
    name: str
    version: str
    seed: int


# ---------------------------------------------------------------------------
# DataConfig
#
# Stores paths for raw telemetry data and processed local storage.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DataConfig:
    raw_events_path: str
    processed_database_path: str


# ---------------------------------------------------------------------------
# GenerationConfig
#
# Stores settings used to generate simulated playtest telemetry.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GenerationConfig:
    player_count: int
    min_sessions_per_player: int
    max_sessions_per_player: int
    level_count: int


# ---------------------------------------------------------------------------
# DashboardConfig
#
# Stores dashboard display settings.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DashboardConfig:
    title: str


# ---------------------------------------------------------------------------
# AppConfig
#
# Groups all project configuration sections into one object.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class AppConfig:
    project: ProjectConfig
    data: DataConfig
    generation: GenerationConfig
    dashboard: DashboardConfig
