# Architecture

This document gives a compact architecture overview for **Playtest Pulse**.

The structure follows a lightweight arc42-style format. It focuses on the information that is useful for a small portfolio project: goals, constraints, module boundaries, runtime flows, storage design, tradeoffs, and common terms.

---

## 1. Introduction and Goals

**Playtest Pulse** is a small local analytics application for simulated game playtest telemetry.

The project generates fictional gameplay events, validates and stores them locally, calculates player behavior metrics, and displays the results in a Streamlit dashboard.

The main goals are:

- generate deterministic simulated playtest telemetry
- validate raw event data before analytics or storage
- persist cleaned telemetry in local SQLite storage
- calculate gameplay metrics using pandas
- display useful playtest insights in a dashboard
- keep responsibilities separated across focused modules
- demonstrate pragmatic, testable software design

Non-goals:

- production telemetry ingestion
- real-time streaming
- cloud deployment
- authentication
- large-scale data storage
- advanced game simulation
- production BI tooling

---

## 2. Constraints

| Constraint | Impact |
|---|---|
| Python | Keeps the project approachable and aligned with analytics workflows. |
| Pandas | Used for tabular metric calculations and dashboard-ready data. |
| SQLite | Provides local persistence without external infrastructure. |
| Streamlit | Provides a simple Python-native dashboard. |
| Simulated data | Keeps the project self-contained and runnable without private game data. |
| Local execution | The project can run from scripts on a developer machine. |
| Small portfolio scope | Architecture should stay clear and useful without becoming overbuilt. |

---

## 3. Solution Strategy

The system is organized around a clear local data pipeline:

    generate simulated telemetry
        -> write raw CSV
        -> load and validate CSV rows
        -> insert validated events into SQLite
        -> query analytics-shaped DataFrame
        -> calculate gameplay metrics
        -> render Streamlit dashboard

The source package is split by responsibility:

| Package | Responsibility |
|---|---|
| `config` | Load and validate project configuration. |
| `domain` | Define the telemetry event model and supported event types. |
| `ingestion` | Generate sample data, validate raw CSV rows, and load CSV files. |
| `analytics` | Convert events to DataFrames and calculate gameplay metrics. |
| `storage` | Own SQLite schema creation, inserts, and queries. |
| `dashboard` | Prepare dashboard data and render the Streamlit UI. |
| `scripts` | Provide user-facing command entry points. |

The design favors plain functions and small classes. Patterns are used only where they clarify boundaries.

---

## 4. System Context

Playtest Pulse runs locally.

The user interacts with the system through command-line scripts and a local Streamlit dashboard. The system reads configuration from YAML, writes generated files to local folders, stores cleaned data in SQLite, and displays analytics in the browser.

There are no external services, cloud resources, message brokers, or game engine integrations.

---

## 5. Container View

This project is not a distributed system, so the C4 "container" concept is used lightly.

    +----------------------------------------------------------------------------------+
    | Playtest Pulse                                                                    |
    |----------------------------------------------------------------------------------|
    | Purpose: generate, store, analyze, and display simulated playtest telemetry        |
    +----------------------------------------------------------------------------------+

        [Developer / Reviewer]
                |
                v
    +-------------------------+       reads/writes        +----------------------------+
    | CLI Scripts             | <-----------------------> | Local Filesystem           |
    |-------------------------|                           |----------------------------|
    | generate_sample_data.py |                           | configs/base.yaml          |
    | ingest_events.py        |                           | data/raw/sample_events.csv |
    | run_dashboard.py        |                           | data/processed/*.sqlite3   |
    +-------------------------+                           +----------------------------+
                |
                v
    +----------------------------------------------------------------------------------+
    | Playtest Pulse Python Application                                                 |
    |----------------------------------------------------------------------------------|
    | config      - configuration loading                                               |
    | domain      - telemetry event model                                               |
    | ingestion   - generation, CSV loading, row validation                             |
    | analytics   - pandas DataFrames and metric calculations                           |
    | storage     - SQLite schema, repository inserts and queries                       |
    | dashboard   - dashboard data preparation and Streamlit rendering                  |
    +----------------------------------------------------------------------------------+
                |
                v
    +-------------------------+
    | Local Browser           |
    |-------------------------|
    | Streamlit dashboard     |
    +-------------------------+

---

## 6. Building Block View

The application is separated by responsibility rather than by one large script.

    +----------------------------------------------------------------------------------+
    | Playtest Pulse Python Application                                                 |
    +----------------------------------------------------------------------------------+

    +------------------+       +------------------+       +---------------------------+
    | config           | ----> | ingestion        | ----> | domain                    |
    |------------------|       |------------------|       |---------------------------|
    | load YAML        |       | generate events  |       | TelemetryEvent            |
    | config schema    |       | load CSV rows    |       | EventTypes                |
    | config errors    |       | validate rows    |       +---------------------------+
    +------------------+       +------------------+
               |                       |
               v                       v
    +------------------+       +------------------+       +---------------------------+
    | storage          | ----> | analytics        | ----> | dashboard                 |
    |------------------|       |------------------|       |---------------------------|
    | SQLite schema    |       | event DataFrame  |       | data service              |
    | repository       |       | session metrics  |       | Streamlit app             |
    | inserts/queries  |       | level metrics    |       | tables and charts         |
    +------------------+       | combat metrics   |       +---------------------------+
                               | item metrics     |
                               +------------------+

---

## 7. Runtime Views

### 7.1 Sample Data Generation

    1. Load config from configs/base.yaml.
    2. Read project seed and generation settings.
    3. Generate deterministic simulated playtest events.
    4. Write raw event rows to data/raw/sample_events.csv.

Entry point:

    python scripts/generate_sample_data.py --config configs/base.yaml

Important boundary:

- sample generation creates event data
- CSV writing happens in the script
- generated CSV output is ignored by Git

### 7.2 CSV Loading and Validation

    1. Open generated CSV file.
    2. Read rows with csv.DictReader.
    3. Validate required raw event columns.
    4. Convert valid raw rows into TelemetryEvent objects.
    5. Raise clear errors for invalid rows.

Important boundary:

- ingestion validates raw CSV shape
- ingestion does not calculate metrics
- ingestion does not define the SQLite schema

### 7.3 SQLite Ingestion

    1. Load config.
    2. Load validated events from CSV.
    3. Open local SQLite database.
    4. Initialize normalized schema.
    5. Insert each event into base and detail tables.
    6. Commit the transaction.
    7. Close the database connection.

Entry point:

    python scripts/ingest_events.py --config configs/base.yaml --replace

Important boundary:

- storage owns SQLite schema and queries
- storage does not know about Streamlit
- storage returns analytics-shaped DataFrames for downstream use

### 7.4 Dashboard Rendering

    1. Load config.
    2. Open local SQLite database.
    3. Query events as a pandas DataFrame.
    4. Calculate dashboard metrics.
    5. Render summary cards, tables, and charts in Streamlit.

Entry point:

    streamlit run scripts/run_dashboard.py -- --config configs/base.yaml

Important boundary:

- dashboard rendering code does not calculate raw metrics directly
- dashboard data service prepares the data
- analytics functions remain independent of Streamlit

---

## 8. Storage Design

The generated CSV uses a wide raw event-log format because it is easy to inspect and easy to generate.

The SQLite storage uses normalized tables so common event fields are separated from event-specific fields.

    +------------------+
    | events           |
    |------------------|
    | event_id         |
    | player_id        |
    | session_id       |
    | timestamp        |
    | event_type       |
    +------------------+
            |
            +----------------------+
            |                      |
            v                      v
    +------------------+   +------------------+
    | session_events   |   | level_events     |
    |------------------|   |------------------|
    | event_id         |   | event_id         |
    | duration_seconds |   | level_id         |
    +------------------+   | result           |
                           | duration_seconds |
                           +------------------+

            +----------------------+----------------------+
            |                                             |
            v                                             v
    +------------------+                         +------------------+
    | combat_events    |                         | item_events      |
    |------------------|                         |------------------|
    | event_id         |                         | event_id         |
    | enemy_type       |                         | item_id          |
    | damage_taken     |                         +------------------+
    | result           |
    +------------------+

This design keeps the local database cleaner than a single wide table while still being simple enough for the project scope.

---

## 9. Cross-Cutting Concepts

### Configuration

Configuration is stored in YAML and loaded into typed config objects. This keeps paths and generation settings visible without scattering constants through scripts.

### Raw Events vs Stored Events

The CSV file is a raw event log. The SQLite database is normalized storage. These are related but not the same design.

### DataFrames

Pandas DataFrames are the standard analytics shape. Metrics operate on DataFrames so the dashboard and storage layer can share one tabular interface.

### Deterministic Sample Data

Sample data generation uses a seed. This makes tests and local demos repeatable.

### Local Persistence

SQLite is used for local persistence because the project does not need a server, cloud database, or separate database setup.

### Testing

Unit tests cover focused logic. Integration tests cover CSV loading and SQLite behavior. End-to-end tests should cover the full local workflow without launching Streamlit.

---

## 10. Architecture Decisions and Tradeoffs

### Simulated playtest telemetry

The project uses generated fictional telemetry so the repo can run without real game data.

Tradeoff:

- easy to run and share
- not a substitute for real production telemetry

### Pandas for analytics

Pandas is used for metric calculations because the project is fundamentally tabular analytics.

Tradeoff:

- strong fit for local analytics
- not designed for very large distributed datasets

### Streamlit for dashboard

Streamlit is used because it keeps dashboard development Python-native and lightweight.

Tradeoff:

- quick and readable
- less control than a custom React frontend

### SQLite for storage

SQLite provides local persistence without requiring external services.

Tradeoff:

- simple and portable
- not intended for large multi-user workloads

### Normalized local storage

The project uses normalized SQLite tables for common and event-specific fields.

Tradeoff:

- cleaner storage design
- slightly more query complexity than one wide table

---

## 11. Risks and Technical Debt

Known limitations:

- sample data is fictional and simplified
- dashboard filters are minimal
- SQLite ingestion is local-only
- no real-time telemetry ingestion exists
- no game engine integration exists
- no authentication or deployment layer exists
- Streamlit UI is intentionally simple
- storage does not include migrations

These are acceptable for the first version. The goal is a clear local analytics workflow, not production telemetry infrastructure.

---

## 12. Glossary

| Term | Meaning |
|---|---|
| Analytics | The process of calculating useful measurements from data. |
| CSV | A comma-separated values file used here as the raw telemetry export format. |
| Dashboard | A visual interface that displays metrics, tables, and charts. |
| DataFrame | A pandas table-like data structure used for analytics. |
| Deterministic data | Data that is generated the same way each time when the same seed is used. |
| Event | One recorded action or occurrence from a simulated playtest session. |
| Event type | The category of event, such as `level_start`, `item_pickup`, or `player_death`. |
| Ingestion | The process of loading raw data into the application. |
| Metric | A calculated value, such as total sessions or average session duration. |
| Normalization | A database design approach that separates repeated or optional data into related tables. |
| Playtest | A session where a game is played to observe behavior, balance, or usability. |
| Repository | A storage component that hides database insert and query details from the rest of the app. |
| SQLite | A lightweight local database stored in a file. |
| Streamlit | A Python library for building simple data dashboards. |
| Telemetry | Event data that records what happened during gameplay or playtesting. |
| Validation | Checking data before using it so invalid rows fail clearly. |

---

## 13. Summary

Playtest Pulse is a small but complete local analytics application.

Its main architectural qualities are:

- clear module boundaries
- deterministic sample data
- validated ingestion
- normalized local storage
- pandas-based metrics
- Streamlit presentation
- focused tests
- lightweight documentation

The project is intentionally pragmatic. It avoids production infrastructure while still showing a complete data workflow from generation to visualization.