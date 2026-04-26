# ADR: Use SQLite for Local Storage

## Status

Accepted

## Context

The project needs a way to persist validated telemetry events after CSV loading.

A server database would add setup and infrastructure that the project does not need.

## Decision

SQLite is used for local telemetry storage.

The database is stored as a local file under the configured processed data path.

## Consequences

This keeps storage simple and portable.

The project can demonstrate persistence and querying without requiring external services.

The tradeoff is that SQLite is not intended for large multi-user telemetry workloads. That is acceptable because this project runs locally.