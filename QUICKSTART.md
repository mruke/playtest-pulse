# Quickstart

This guide explains how to run **Playtest Pulse** locally.

The project generates simulated playtest telemetry, loads the generated CSV data, calculates gameplay metrics, and displays the results in a Streamlit dashboard.

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

## 4. Run the dashboard

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

## 5. Run tests

Run the full test suite:

    pytest

## Notes

The first version uses generated sample data and local files. SQLite storage, SQLAlchemy evaluation, real-time event ingestion, and a possible PySide6 desktop dashboard are future extension ideas rather than part of the first dashboard slice.