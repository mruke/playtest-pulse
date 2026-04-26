from __future__ import annotations

import sqlite3

from playtest_pulse.storage import TABLE_NAMES, initialize_schema


# ---------------------------------------------------------------------------
# _table_names
#
# Reads the user-created table names from a SQLite connection.
# ---------------------------------------------------------------------------
def _table_names(connection: sqlite3.Connection) -> set[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%';
        """
    ).fetchall()

    return {row[0] for row in rows}


# ---------------------------------------------------------------------------
# test_initialize_schema_creates_expected_tables
#
# Verifies that schema initialization creates all telemetry storage tables.
# ---------------------------------------------------------------------------
def test_initialize_schema_creates_expected_tables() -> None:
    connection = sqlite3.connect(":memory:")

    initialize_schema(connection)

    assert _table_names(connection) == set(TABLE_NAMES)


# ---------------------------------------------------------------------------
# test_initialize_schema_is_idempotent
#
# Verifies that schema initialization can safely run more than once.
# ---------------------------------------------------------------------------
def test_initialize_schema_is_idempotent() -> None:
    connection = sqlite3.connect(":memory:")

    initialize_schema(connection)
    initialize_schema(connection)

    assert _table_names(connection) == set(TABLE_NAMES)


# ---------------------------------------------------------------------------
# test_initialize_schema_enables_foreign_keys
#
# Verifies that foreign key enforcement is enabled for the connection.
# ---------------------------------------------------------------------------
def test_initialize_schema_enables_foreign_keys() -> None:
    connection = sqlite3.connect(":memory:")

    initialize_schema(connection)

    pragma_value = connection.execute("PRAGMA foreign_keys;").fetchone()[0]

    assert pragma_value == 1
