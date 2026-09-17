import sqlite3

import pytest

from app.database import Database


def test_database_rejects_event_for_missing_ticket(tmp_path) -> None:
    database = Database(str(tmp_path / "support_tickets.db"))
    database.initialize()

    with pytest.raises(sqlite3.IntegrityError):
        with database.connect() as connection:
            connection.execute(
                """
                INSERT INTO ticket_events (ticket_id, event_type, detail, created_at)
                VALUES (999, 'created', 'test event', '2026-01-01T09:00:00+00:00')
                """
            )
