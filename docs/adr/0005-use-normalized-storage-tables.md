# ADR: Use Normalized Storage Tables

## Status

Accepted

## Context

The generated CSV uses a wide raw event-log format.

That format is easy to generate and inspect, but it is not the cleanest shape for relational storage because many fields only apply to certain event types.

## Decision

SQLite storage uses normalized tables.

Common event fields are stored in `events`. Event-specific fields are stored in detail tables such as `session_events`, `level_events`, `combat_events`, and `item_events`.

## Consequences

This creates a cleaner local database design.

It separates common event data from event-specific data and better reflects relational design.

The tradeoff is that queries need joins to rebuild an analytics-ready event table. This is acceptable because the repository owns that query logic.