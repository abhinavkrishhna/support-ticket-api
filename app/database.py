"""Database setup for the app."""

from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


class Database:
    def __init__(self, path: str) -> None:
        self.path = path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        except Exception:
            connection.rollback()
            raise
        finally:
            connection.close()

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    requester_email TEXT NOT NULL,
                    category TEXT NOT NULL,
                    team TEXT NOT NULL,
                    priority TEXT NOT NULL CHECK(priority IN ('low', 'medium', 'high', 'urgent')),
                    status TEXT NOT NULL CHECK(status IN ('new', 'in_progress', 'resolved')),
                    assignee TEXT,
                    created_at TEXT NOT NULL,
                    due_at TEXT NOT NULL,
                    resolved_at TEXT
                );

                CREATE TABLE IF NOT EXISTS ticket_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER NOT NULL,
                    event_type TEXT NOT NULL,
                    detail TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(ticket_id) REFERENCES tickets(id)
                );

                CREATE INDEX IF NOT EXISTS idx_tickets_status_due
                    ON tickets(status, due_at);
                CREATE INDEX IF NOT EXISTS idx_tickets_team
                    ON tickets(team);
                CREATE INDEX IF NOT EXISTS idx_ticket_events_ticket
                    ON ticket_events(ticket_id, created_at);
                """
            )
