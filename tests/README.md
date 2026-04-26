# Test Suite

The test suite is organized by test type.

## Structure

| Directory | Purpose |
|---|---|
| `unit/` | Focused tests for functions, domain objects, validation, analytics metrics, and dashboard data preparation. |
| `integration/` | Tests that involve file loading, CSV parsing, SQLite schema behavior, or repository behavior. |
| `e2e/` | End-to-end workflow tests that verify multiple project layers working together. |
| `helpers/` | Shared test support code. This directory is not a test category by itself. |

## Current Focus

The current suite focuses on:

- config loading
- telemetry event validation
- sample data generation
- CSV loading
- pandas analytics metrics
- SQLite schema and repository behavior
- dashboard data preparation

## Running Tests

Run the full suite from the repository root:

    pytest