
# Playtest Pulse

A small Python analytics dashboard for simulated game playtest telemetry.

The project generates fictional gameplay event data, stores it locally in SQLite, calculates player behavior metrics, and displays design-focused insights in a Streamlit dashboard.

## Purpose

This project explores how game telemetry can be used to understand player behavior during playtesting.

It focuses on questions such as:

- How long are player sessions?
- Which levels have the highest failure rate?
- Where do player deaths happen most often?
- Which items are picked up most frequently?
- How many players return for multiple sessions?

## Planned Scope

The first version will include:

- simulated gameplay telemetry data
- CSV ingestion
- local SQLite storage
- gameplay metric calculations
- a Streamlit dashboard
- unit, integration, and end-to-end tests
- architecture documentation and ADRs

## Implementation Steps

The project will be built in small, focused steps. Each step should leave the repository in a working state and add one clear piece of functionality.

| Step | Focus Area | Goal | Status |
|---|---|---|---|
| 1 | Sample data generation | Generate deterministic simulated playtest telemetry as CSV data. | Planned |
| 2 | Data loading and validation | Load telemetry CSV files and reject invalid or malformed event rows. | Planned |
| 3 | Analytics metrics | Calculate player, session, level, combat, and item usage metrics. | Planned |
| 4 | Dashboard | Display gameplay insights in a small Streamlit dashboard. | Planned |
| 5 | Local storage | Persist cleaned telemetry data in SQLite and query it for analysis. | Planned |
| 6 | Documentation and polish | Add usage docs, architecture notes, ADRs, tests documentation, and final cleanup. | Planned |

## Tech Stack

- Python
- Pandas
- SQLite
- Streamlit
- pytest

## Project Status

Planned.

