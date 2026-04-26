from __future__ import annotations

from pathlib import Path
import sqlite3

import pandas as pd

from playtest_pulse.domain import EventTypes, TelemetryEvent
from playtest_pulse.storage.schema import initialize_schema


# ---------------------------------------------------------------------------
# TelemetryRepository
#
# Stores and queries validated telemetry events in normalized SQLite tables.
# ---------------------------------------------------------------------------
class TelemetryRepository:
    # -----------------------------------------------------------------------
    # __init__
    #
    # Opens the SQLite database and ensures the telemetry schema exists.
    # -----------------------------------------------------------------------
    def __init__(self, database_path: str | Path) -> None:
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        initialize_schema(self.connection)

    # -----------------------------------------------------------------------
    # close
    #
    # Closes the repository database connection.
    # -----------------------------------------------------------------------
    def close(self) -> None:
        self.connection.close()

    # -----------------------------------------------------------------------
    # insert_events
    #
    # Inserts validated telemetry events into normalized storage tables.
    # -----------------------------------------------------------------------
    def insert_events(self, events: list[TelemetryEvent]) -> None:
        if not events:
            raise ValueError("events must contain at least one TelemetryEvent.")

        for event in events:
            self._insert_event(event)

        self.connection.commit()

    # -----------------------------------------------------------------------
    # fetch_events_frame
    #
    # Returns stored telemetry events as a pandas DataFrame for analytics.
    # -----------------------------------------------------------------------
    def fetch_events_frame(self) -> pd.DataFrame:
        query = """
        SELECT
            events.event_id,
            events.player_id,
            events.session_id,
            events.timestamp,
            events.event_type,
            level_events.level_id,
            combat_events.enemy_type,
            item_events.item_id,
            COALESCE(
                session_events.duration_seconds,
                level_events.duration_seconds
            ) AS duration_seconds,
            combat_events.damage_taken,
            COALESCE(level_events.result, combat_events.result) AS result
        FROM events
        LEFT JOIN session_events
            ON events.event_id = session_events.event_id
        LEFT JOIN level_events
            ON events.event_id = level_events.event_id
        LEFT JOIN combat_events
            ON events.event_id = combat_events.event_id
        LEFT JOIN item_events
            ON events.event_id = item_events.event_id
        ORDER BY events.timestamp, events.event_id;
        """

        frame = pd.read_sql_query(query, self.connection)
        frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="raise")

        return frame

    # -----------------------------------------------------------------------
    # count_events
    #
    # Counts rows in the base events table.
    # -----------------------------------------------------------------------
    def count_events(self) -> int:
        row = self.connection.execute(
            "SELECT COUNT(*) AS count FROM events;"
        ).fetchone()

        return int(row["count"])

    # -----------------------------------------------------------------------
    # _insert_event
    #
    # Inserts one event into the base event table and any matching detail table.
    # -----------------------------------------------------------------------
    def _insert_event(self, event: TelemetryEvent) -> None:
        self.connection.execute(
            """
            INSERT INTO events (
                event_id,
                player_id,
                session_id,
                timestamp,
                event_type
            )
            VALUES (?, ?, ?, ?, ?);
            """,
            (
                event.event_id,
                event.player_id,
                event.session_id,
                event.timestamp,
                event.event_type,
            ),
        )

        if event.event_type == EventTypes.SESSION_END:
            self._insert_session_event(event)

        if event.event_type in _LEVEL_EVENT_TYPES:
            self._insert_level_event(event)

        if event.event_type in _COMBAT_EVENT_TYPES:
            self._insert_combat_event(event)

        if event.event_type == EventTypes.ITEM_PICKUP:
            self._insert_item_event(event)

    # -----------------------------------------------------------------------
    # _insert_session_event
    #
    # Inserts session-specific fields for session end events.
    # -----------------------------------------------------------------------
    def _insert_session_event(self, event: TelemetryEvent) -> None:
        self.connection.execute(
            """
            INSERT INTO session_events (
                event_id,
                duration_seconds
            )
            VALUES (?, ?);
            """,
            (
                event.event_id,
                event.duration_seconds,
            ),
        )

    # -----------------------------------------------------------------------
    # _insert_level_event
    #
    # Inserts level-specific fields for level-related event types.
    # -----------------------------------------------------------------------
    def _insert_level_event(self, event: TelemetryEvent) -> None:
        if event.level_id is None:
            return

        self.connection.execute(
            """
            INSERT INTO level_events (
                event_id,
                level_id,
                result,
                duration_seconds
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                event.event_id,
                event.level_id,
                event.result,
                event.duration_seconds,
            ),
        )

    # -----------------------------------------------------------------------
    # _insert_combat_event
    #
    # Inserts combat-specific fields for combat-related event types.
    # -----------------------------------------------------------------------
    def _insert_combat_event(self, event: TelemetryEvent) -> None:
        self.connection.execute(
            """
            INSERT INTO combat_events (
                event_id,
                enemy_type,
                damage_taken,
                result
            )
            VALUES (?, ?, ?, ?);
            """,
            (
                event.event_id,
                event.enemy_type,
                event.damage_taken,
                event.result,
            ),
        )

    # -----------------------------------------------------------------------
    # _insert_item_event
    #
    # Inserts item-specific fields for item pickup events.
    # -----------------------------------------------------------------------
    def _insert_item_event(self, event: TelemetryEvent) -> None:
        if event.item_id is None:
            return

        self.connection.execute(
            """
            INSERT INTO item_events (
                event_id,
                item_id
            )
            VALUES (?, ?);
            """,
            (
                event.event_id,
                event.item_id,
            ),
        )


_LEVEL_EVENT_TYPES = {
    EventTypes.LEVEL_START,
    EventTypes.LEVEL_COMPLETE,
    EventTypes.LEVEL_FAIL,
    EventTypes.PLAYER_DEATH,
    EventTypes.ITEM_PICKUP,
    EventTypes.ENEMY_DEFEATED,
}

_COMBAT_EVENT_TYPES = {
    EventTypes.PLAYER_DEATH,
    EventTypes.ENEMY_DEFEATED,
}
