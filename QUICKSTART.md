# Quickstart

This guide explains how to run **Playtest Pulse** locally.

The project generates simulated playtest telemetry, loads the generated CSV data into SQLite, calculates gameplay metrics, and displays the results in a Streamlit dashboard.

## 1. Create a virtual environment

From the repository root:

    python -m venv .venv

Activate it in PowerShell:

    .\.venv\Scripts\Activate.ps1

## 2. Install dependencies

Install the project and development dependencies:

    pip install -e ".[dev]"

## 3. Generate sample telemetry

Create deterministic sample playtest data:

    python scripts/generate_sample_data.py --config configs/base.yaml

This writes a CSV file to:

    data/raw/sample_events.csv

The generated CSV is ignored by Git.

## 4. Load telemetry into SQLite

Persist the generated telemetry CSV into local SQLite storage:

    python scripts/ingest_events.py --config configs/base.yaml --replace

This writes a SQLite database to:

    data/processed/telemetry.sqlite3

The `--replace` flag makes the workflow repeatable by replacing the existing local database before ingestion.

## 5. Run the dashboard

Start the Streamlit dashboard:

    streamlit run scripts/run_dashboard.py -- --config configs/base.yaml

The dashboard shows:

- player and session summary metrics
- level completion and failure rates
- deaths by level
- enemy defeats
- average damage taken
- item pickup counts
- raw event data

## 6. Run tests

Run the full test suite:

    pytest

## Notes

Generated local files are ignored by Git:

    data/raw/sample_events.csv
    data/processed/telemetry.sqlite3

The first version uses generated sample data, local SQLite storage, pandas analytics, and a Streamlit dashboard.