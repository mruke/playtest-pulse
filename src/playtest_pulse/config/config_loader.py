from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from playtest_pulse.config.config_exceptions import ConfigError
from playtest_pulse.config.config_schema import (
    AppConfig,
    DashboardConfig,
    DataConfig,
    GenerationConfig,
    ProjectConfig,
)


# ---------------------------------------------------------------------------
# load_config
#
# Loads a YAML configuration file and returns a validated AppConfig object.
# ---------------------------------------------------------------------------
def load_config(config_path: str | Path) -> AppConfig:
    path = Path(config_path)

    if not path.is_file():
        raise ConfigError(f"Config file does not exist: {path}")

    try:
        raw_config = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise ConfigError(f"Config file is not valid YAML: {path}") from error

    if not isinstance(raw_config, dict):
        raise ConfigError("Config file must contain a YAML mapping.")

    project = _require_section(raw_config, "project")
    data = _require_section(raw_config, "data")
    generation = _require_section(raw_config, "generation")
    dashboard = _require_section(raw_config, "dashboard")

    config = AppConfig(
        project=ProjectConfig(
            name=_require_value(project, "name", str),
            version=_require_value(project, "version", str),
            seed=_require_value(project, "seed", int),
        ),
        data=DataConfig(
            raw_events_path=_require_value(data, "raw_events_path", str),
            processed_database_path=_require_value(
                data,
                "processed_database_path",
                str,
            ),
        ),
        generation=GenerationConfig(
            player_count=_require_value(generation, "player_count", int),
            min_sessions_per_player=_require_value(
                generation,
                "min_sessions_per_player",
                int,
            ),
            max_sessions_per_player=_require_value(
                generation,
                "max_sessions_per_player",
                int,
            ),
            level_count=_require_value(generation, "level_count", int),
        ),
        dashboard=DashboardConfig(
            title=_require_value(dashboard, "title", str),
        ),
    )

    _validate_config(config)

    return config


# ---------------------------------------------------------------------------
# _require_section
#
# Reads a required mapping section from the raw config.
# ---------------------------------------------------------------------------
def _require_section(raw_config: dict[str, Any], section_name: str) -> dict[str, Any]:
    section = raw_config.get(section_name)

    if not isinstance(section, dict):
        raise ConfigError(f"Missing or invalid config section: {section_name}")

    return section


# ---------------------------------------------------------------------------
# _require_value
#
# Reads a required config value and checks its expected type.
# ---------------------------------------------------------------------------
def _require_value(
    section: dict[str, Any],
    key: str,
    expected_type: type,
) -> Any:
    value = section.get(key)

    if not isinstance(value, expected_type):
        raise ConfigError(f"Missing or invalid config value: {key}")

    if isinstance(value, str) and not value.strip():
        raise ConfigError(f"Config string cannot be empty: {key}")

    if isinstance(value, int) and value <= 0:
        raise ConfigError(f"Config integer must be positive: {key}")

    return value


# ---------------------------------------------------------------------------
# _validate_config
#
# Validates cross-field rules that involve more than one config value.
# ---------------------------------------------------------------------------
def _validate_config(config: AppConfig) -> None:
    if (
        config.generation.min_sessions_per_player
        > config.generation.max_sessions_per_player
    ):
        raise ConfigError(
            "min_sessions_per_player cannot be greater than max_sessions_per_player."
        )
