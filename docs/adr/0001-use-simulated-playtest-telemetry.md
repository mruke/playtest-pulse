# ADR: Use Simulated Playtest Telemetry

## Status

Accepted

## Context

This project needs telemetry data to demonstrate loading, validation, storage, analytics, and dashboard behavior.

Using real game telemetry would require access to private or production data. That would make the project harder to run and harder to share.

## Decision

Simulated playtest telemetry is used for the first version.

The project generates fictional gameplay events from local configuration.

## Consequences

The project is self-contained and easy to run.

The generated data can be deterministic, which helps testing and demos.

The tradeoff is that the data is simplified. It does not represent the full complexity of real gameplay telemetry.