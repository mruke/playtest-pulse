from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from pathlib import Path

from playtest_pulse.config import load_config
from playtest_pulse.domain import TelemetryEvent
from playtest_pulse.ingestion import generate_sample_events


# ---------------------------------------------------------------------------
# main
#
# Loads config, generates sample telemetry, and writes it to a CSV file.
# ---------------------------------------------------------------------------
def main() -> None:
    args = _parse_args()
    config = load_config(args.config)

    events = generate_sample_events(
        project_config=config.project,
        generation_config=config.generation,
    )

    output_path = Path(config.data.raw_events_path)
    _write_events_csv(output_path, events)

    print(f"Wrote {len(events)} events to {output_path}")


# ---------------------------------------------------------------------------
# _parse_args
#
# Reads command-line arguments for the sample data generation script.
# ---------------------------------------------------------------------------
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate simulated playtest telemetry data.",
    )
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Path to the YAML config file.",
    )

    return parser.parse_args()


# ---------------------------------------------------------------------------
# _write_events_csv
#
# Writes generated telemetry events to a CSV file with a header row.
# ---------------------------------------------------------------------------
def _write_events_csv(
    output_path: Path,
    events: list[TelemetryEvent],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "event_id",
        "player_id",
        "session_id",
        "timestamp",
        "event_type",
        "level_id",
        "enemy_type",
        "item_id",
        "duration_seconds",
        "damage_taken",
        "result",
    ]

    with output_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()

        for event in events:
            writer.writerow(asdict(event))


if __name__ == "__main__":
    main()
