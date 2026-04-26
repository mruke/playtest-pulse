# ADR: Use Streamlit for the Dashboard

## Status

Accepted

## Context

The project needs a dashboard to show gameplay metrics and make the analytics visible.

A custom frontend would require more setup, routing, API design, and JavaScript code.

## Decision

Streamlit is used for the dashboard.

The dashboard is written in Python and displays summary metrics, tables, and charts.

## Consequences

This keeps the dashboard simple and easy to run locally.

It allows the project to focus on the data workflow instead of frontend infrastructure.

The tradeoff is that Streamlit gives less control than a custom React interface. That is acceptable for the first version.