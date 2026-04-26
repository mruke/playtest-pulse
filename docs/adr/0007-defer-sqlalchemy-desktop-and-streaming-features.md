# ADR: Defer SQLAlchemy, Desktop UI, and Real-Time Streaming

## Status

Accepted

## Context

Several possible extensions were considered, including SQLAlchemy, a PySide6 desktop dashboard, and real-time telemetry ingestion.

These could be useful later, but they would increase the scope of the first version.

## Decision

SQLAlchemy, PySide6, and real-time streaming are deferred.

The first version uses built-in `sqlite3`, Streamlit, local files, and generated telemetry.

## Consequences

This keeps the project focused and easier to complete.

It also keeps the first version centered on the core data workflow: generation, validation, storage, analytics, and visualization.

The tradeoff is that the project does not yet demonstrate ORM usage, desktop UI development, or live event streaming. Those remain possible future extensions.