from __future__ import annotations

import argparse

from playtest_pulse.config import load_config
from playtest_pulse.ingestion import load_events_csv
from playtest_pulse.storage import TelemetryRepository


# ---------------------------------------------------------------------------
# main
#
# Loads generated telemetry CSV data and persists it in local SQLite storage.
# ---------------------------------------------------------------------------
def main() -> None:
    args = _parse_args()
    config = load_config(args.config)

    events = load_events_csv(config.data.raw_events_path)
    repository = TelemetryRepository(config.data.processed_database_path)

    try:
        repository.insert_events(events)
        event_count = repository.count_events()
    finally:
        repository.close()

    print(
        "Stored "
        f"{len(events)} events in {config.data.processed_database_path}. "
        f"Database now contains {event_count} events."
    )


# ---------------------------------------------------------------------------
# _parse_args
#
# Reads command-line arguments for local telemetry storage ingestion.
# ---------------------------------------------------------------------------
def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load generated telemetry CSV data into local SQLite storage.",
    )
    parser.add_argument(
        "--config",
        default="configs/base.yaml",
        help="Path to the YAML config file.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
