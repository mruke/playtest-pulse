# ADR: Use Pandas for Analytics

## Status

Accepted

## Context

The project calculates metrics from tabular telemetry data.

These metrics include session counts, level completion rates, deaths by level, enemy defeats, and item pickup counts.

## Decision

Pandas is used for analytics.

Telemetry events are converted into DataFrames, and metric functions accept DataFrames as input.

## Consequences

This keeps analytics code practical and readable.

It also fits well with Streamlit, which can display DataFrames directly.

The tradeoff is that pandas is intended for local data analysis, not distributed analytics at production scale. That is acceptable for this local portfolio project.