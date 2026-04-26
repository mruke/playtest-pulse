from __future__ import annotations

import csv
from dataclasses import asdict
from pathlib import Path

from playtest_pulse.domain import RAW_EVENT_COLUMNS, TelemetryEvent


# ---------------------------------------------------------------------------
# write_events_csv
#
# Writes telemetry events to a CSV file using the raw event column order.
# ---------------------------------------------------------------------------
def write_events_csv(csv_path: Path, events: list[TelemetryEvent]) -> Path:
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with csv_path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=RAW_EVENT_COLUMNS)
        writer.writeheader()

        for event in events:
            writer.writerow(asdict(event))

    return csv_path
