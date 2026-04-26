# Playtest Pulse

A small Python analytics dashboard for simulated game playtest telemetry.

The project generates fictional gameplay event data, validates and stores it locally, calculates player behavior metrics, and displays design-focused insights in a Streamlit dashboard.

## Purpose

This project explores how game telemetry can be used to understand player behavior during playtesting.

It focuses on questions such as:

- How long are player sessions?
- Which levels have the highest failure rate?
- Where do player deaths happen most often?
- Which enemies are defeated most often?
- Which items are picked up most frequently?
- How many players return for multiple sessions?

## What This Project Demonstrates

Playtest Pulse is designed as an end-to-end local analytics application.

It demonstrates:

- simulated event-data generation
- CSV loading and validation
- normalized SQLite persistence
- pandas-based analytics
- Streamlit dashboard presentation
- unit and integration testing
- modular project structure
- documented architecture and design decisions

## Scope

The first version includes:

- deterministic simulated playtest telemetry data
- CSV ingestion and raw event row validation
- local SQLite storage using Python's built-in `sqlite3` module
- normalized storage tables for common and event-specific data
- gameplay metric calculations with pandas
- a Streamlit dashboard
- unit and integration tests
- architecture documentation and ADRs

## Implementation Steps

The project is built in small, focused steps. Each step leaves the repository in a working state and adds one clear piece of functionality.

| Step | Focus Area | Goal | Status |
|---|---|---|---|
| 1 | Sample data generation | Generate deterministic simulated playtest telemetry as CSV data. | Complete |
| 2 | Data loading and validation | Load telemetry CSV files and reject invalid or malformed event rows. | Complete |
| 3 | Analytics metrics | Calculate player, session, level, combat, and item usage metrics. | Complete |
| 4 | Dashboard | Display gameplay insights in a small Streamlit dashboard. | Complete |
| 5 | Local storage | Persist cleaned telemetry data in SQLite and query it for analysis. | Complete |
| 6 | Documentation and polish | Add usage docs, architecture notes, ADRs, tests documentation, and final cleanup. | In Progress |

## Tech Stack

- Python
- Pandas
- SQLite
- Streamlit
- PyYAML
- pytest

## Project Structure

    playtest-pulse/
    ├── README.md
    ├── QUICKSTART.md
    ├── ARCHITECTURE.md
    ├── LICENSE
    ├── pyproject.toml
    ├── configs/
    │   └── base.yaml
    ├── data/
    │   ├── raw/
    │   └── processed/
    ├── docs/
    │   └── adr/
    ├── scripts/
    │   ├── generate_sample_data.py
    │   ├── ingest_events.py
    │   └── run_dashboard.py
    ├── src/
    │   └── playtest_pulse/
    │       ├── config/
    │       ├── domain/
    │       ├── ingestion/
    │       ├── analytics/
    │       ├── storage/
    │       ├── dashboard/
    │       └── utils/
    └── tests/
        ├── unit/
        ├── integration/
        ├── e2e/
        └── helpers/

## Usage

See [`QUICKSTART.md`](QUICKSTART.md) for local setup and run instructions.

The basic workflow is:

1. Generate sample telemetry.
2. Load the generated CSV into SQLite.
3. Run the Streamlit dashboard.
4. Run the test suite.

## Architecture

See [`ARCHITECTURE.md`](ARCHITECTURE.md) for the project architecture, runtime flows, storage design, and glossary.

## Future Extensions

Possible follow-up work after the first version:

- Evaluate SQLAlchemy if the storage layer grows beyond simple local tables and queries.
- Explore a PySide6 desktop dashboard if the project becomes more focused on local desktop tooling.
- Add real-time telemetry ingestion later if the project needs to simulate live game events.
- Add dashboard filters for level, event type, or player/session groups.
- Add richer playtest reports or exported summaries.
- Add more realistic simulated player behavior patterns.

## License

This project is licensed under the MIT License. See [`LICENSE`](LICENSE) for details.

## Project Status

Working local prototype. Documentation and polish are in progress.

