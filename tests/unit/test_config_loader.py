from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from playtest_pulse.config import AppConfig, ConfigError, load_config


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _valid_config_dict() -> dict:
    return {
        "project": {
            "name": "playtest-pulse",
            "version": "0.1.0",
            "seed": 42,
        },
        "data": {
            "raw_events_path": "data/raw/sample_events.csv",
            "processed_database_path": "data/processed/telemetry.sqlite3",
        },
        "generation": {
            "player_count": 100,
            "min_sessions_per_player": 1,
            "max_sessions_per_player": 5,
            "level_count": 8,
        },
        "dashboard": {
            "title": "Playtest Pulse",
        },
    }


def _write_yaml(tmp_path: Path, content: dict) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(content), encoding="utf-8")
    return config_path


# ---------------------------------------------------------------------------
# test_load_base_config_returns_app_config
#
# Verifies that the real base config file loads into an AppConfig object.
# ---------------------------------------------------------------------------
def test_load_base_config_returns_app_config() -> None:
    config = load_config(_repo_root() / "configs" / "base.yaml")

    assert isinstance(config, AppConfig)
    assert config.project.name == "playtest-pulse"
    assert config.project.version == "0.1.0"
    assert config.project.seed == 42
    assert config.data.raw_events_path == "data/raw/sample_events.csv"
    assert config.data.processed_database_path == "data/processed/telemetry.sqlite3"
    assert config.generation.player_count == 100
    assert config.generation.min_sessions_per_player == 1
    assert config.generation.max_sessions_per_player == 5
    assert config.generation.level_count == 8
    assert config.dashboard.title == "Playtest Pulse"


# ---------------------------------------------------------------------------
# test_load_config_rejects_missing_file
#
# Verifies that missing config files fail clearly.
# ---------------------------------------------------------------------------
def test_load_config_rejects_missing_file() -> None:
    with pytest.raises(ConfigError, match="does not exist"):
        load_config("configs/does-not-exist.yaml")


# ---------------------------------------------------------------------------
# test_load_config_rejects_missing_section
#
# Verifies that required top-level config sections must exist.
# ---------------------------------------------------------------------------
def test_load_config_rejects_missing_section(tmp_path: Path) -> None:
    config_dict = _valid_config_dict()
    del config_dict["generation"]

    config_path = _write_yaml(tmp_path, config_dict)

    with pytest.raises(ConfigError, match="generation"):
        load_config(config_path)


# ---------------------------------------------------------------------------
# test_load_config_rejects_invalid_value_type
#
# Verifies that required values must use the expected type.
# ---------------------------------------------------------------------------
def test_load_config_rejects_invalid_value_type(tmp_path: Path) -> None:
    config_dict = _valid_config_dict()
    config_dict["generation"]["player_count"] = "100"

    config_path = _write_yaml(tmp_path, config_dict)

    with pytest.raises(ConfigError, match="player_count"):
        load_config(config_path)


# ---------------------------------------------------------------------------
# test_load_config_rejects_empty_string
#
# Verifies that required string values cannot be empty.
# ---------------------------------------------------------------------------
def test_load_config_rejects_empty_string(tmp_path: Path) -> None:
    config_dict = _valid_config_dict()
    config_dict["project"]["name"] = ""

    config_path = _write_yaml(tmp_path, config_dict)

    with pytest.raises(ConfigError, match="name"):
        load_config(config_path)


# ---------------------------------------------------------------------------
# test_load_config_rejects_non_positive_integer
#
# Verifies that required integer values must be positive.
# ---------------------------------------------------------------------------
def test_load_config_rejects_non_positive_integer(tmp_path: Path) -> None:
    config_dict = _valid_config_dict()
    config_dict["generation"]["player_count"] = 0

    config_path = _write_yaml(tmp_path, config_dict)

    with pytest.raises(ConfigError, match="player_count"):
        load_config(config_path)


# ---------------------------------------------------------------------------
# test_load_config_rejects_invalid_session_range
#
# Verifies that min sessions cannot be greater than max sessions.
# ---------------------------------------------------------------------------
def test_load_config_rejects_invalid_session_range(tmp_path: Path) -> None:
    config_dict = _valid_config_dict()
    config_dict["generation"]["min_sessions_per_player"] = 6
    config_dict["generation"]["max_sessions_per_player"] = 5

    config_path = _write_yaml(tmp_path, config_dict)

    with pytest.raises(ConfigError, match="min_sessions_per_player"):
        load_config(config_path)
