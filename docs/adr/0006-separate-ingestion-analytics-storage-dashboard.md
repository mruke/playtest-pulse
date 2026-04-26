# ADR: Separate Ingestion, Analytics, Storage, and Dashboard Layers

## Status

Accepted

## Context

The project has several different responsibilities: loading data, validating rows, calculating metrics, storing events, and rendering a dashboard.

Putting these responsibilities into one script or one dashboard file would make the project harder to test and maintain.

## Decision

The project separates responsibilities into focused packages.

Ingestion handles generation, CSV loading, and row validation. Analytics handles metric calculations. Storage handles SQLite schema and repository behavior. Dashboard code handles data preparation and Streamlit rendering.

## Consequences

The code is easier to understand and test.

Each package has a clear reason to exist.

The tradeoff is that the project has more files than a single-script dashboard. This is acceptable because the boundaries make the data workflow clearer.