from __future__ import annotations

import csv
from pathlib import Path

from playtest_pulse.domain import TelemetryEvent
from playtest_pulse.ingestion.event_validation import validate_raw_event_row


# ---------------------------------------------------------------------------
# load_events_csv
#
# Loads a telemetry CSV file and returns validated TelemetryEvent objects.
# ---------------------------------------------------------------------------
def load_events_csv(csv_path: str | Path) -> list[TelemetryEvent]:
    path = Path(csv_path)

    if not path.is_file():
        raise FileNotFoundError(f"Telemetry CSV file does not exist: {path}")

    events: list[TelemetryEvent] = []

    with path.open("r", encoding="utf-8", newline="") as csv_file:
        reader = csv.DictReader(csv_file)

        if reader.fieldnames is None:
            raise ValueError(f"Telemetry CSV file has no header row: {path}")

        for row_number, row in enumerate(reader, start=2):
            try:
                events.append(validate_raw_event_row(row))
            except ValueError as error:
                raise ValueError(
                    f"Invalid telemetry row {row_number} in {path}: {error}"
                ) from error

    return events
