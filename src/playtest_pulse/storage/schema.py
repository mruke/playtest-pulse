from __future__ import annotations

import sqlite3


CREATE_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    session_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    event_type TEXT NOT NULL
);
"""

CREATE_LEVEL_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS level_events (
    event_id TEXT PRIMARY KEY,
    level_id TEXT NOT NULL,
    result TEXT,
    duration_seconds INTEGER,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
"""

CREATE_COMBAT_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS combat_events (
    event_id TEXT PRIMARY KEY,
    enemy_type TEXT,
    damage_taken INTEGER,
    result TEXT,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
"""

CREATE_ITEM_EVENTS_TABLE = """
CREATE TABLE IF NOT EXISTS item_events (
    event_id TEXT PRIMARY KEY,
    item_id TEXT NOT NULL,
    FOREIGN KEY (event_id) REFERENCES events(event_id)
);
"""

TABLE_NAMES = [
    "events",
    "level_events",
    "combat_events",
    "item_events",
]


# ---------------------------------------------------------------------------
# initialize_schema
#
# Creates the normalized telemetry storage tables if they do not already exist.
# ---------------------------------------------------------------------------
def initialize_schema(connection: sqlite3.Connection) -> None:
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute(CREATE_EVENTS_TABLE)
    connection.execute(CREATE_LEVEL_EVENTS_TABLE)
    connection.execute(CREATE_COMBAT_EVENTS_TABLE)
    connection.execute(CREATE_ITEM_EVENTS_TABLE)
    connection.commit()
