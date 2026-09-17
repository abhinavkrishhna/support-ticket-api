"""Database queries for tickets."""

from __future__ import annotations

from datetime import datetime

from app.database import Database
from app.models import Ticket, TicketEvent, TicketPriority, TicketStatus


class TicketNotFoundError(LookupError):
    """The ticket was not found."""


class TicketRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def create(
        self,
        *,
        title: str,
        description: str,
        requester_email: str,
        category: str,
        team: str,
        priority: TicketPriority,
        created_at: datetime,
        due_at: datetime,
    ) -> Ticket:
        with self.database.connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO tickets (
                    title, description, requester_email, category, team, priority,
                    status, created_at, due_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    title,
                    description,
                    requester_email,
                    category,
                    team,
                    priority.value,
                    TicketStatus.NEW.value,
                    created_at.isoformat(),
                    due_at.isoformat(),
                ),
            )
            ticket_id = int(cursor.lastrowid)
            self._add_event(
                connection,
                ticket_id,
                "created",
                f"Created in {team} as {category}. Priority: {priority.value}.",
                created_at,
            )
            row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return Ticket.from_row(row)

    def get(self, ticket_id: int) -> Ticket:
        with self.database.connect() as connection:
            row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        if row is None:
            raise TicketNotFoundError(f"Ticket {ticket_id} does not exist.")
        return Ticket.from_row(row)

    def list(
        self, status: TicketStatus | None = None, team: str | None = None, limit: int = 100
    ) -> list[Ticket]:
        clauses: list[str] = []
        values: list[object] = []
        if status:
            clauses.append("status = ?")
            values.append(status.value)
        if team:
            clauses.append("team = ?")
            values.append(team)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        values.append(limit)
        with self.database.connect() as connection:
            rows = connection.execute(
                f"SELECT * FROM tickets {where} ORDER BY due_at ASC LIMIT ?", values
            ).fetchall()
        return [Ticket.from_row(row) for row in rows]

    def update_status(
        self, ticket_id: int, status: TicketStatus, changed_at: datetime
    ) -> Ticket:
        resolved_at = changed_at.isoformat() if status is TicketStatus.RESOLVED else None
        with self.database.connect() as connection:
            cursor = connection.execute(
                "UPDATE tickets SET status = ?, resolved_at = ? WHERE id = ?",
                (status.value, resolved_at, ticket_id),
            )
            if cursor.rowcount == 0:
                raise TicketNotFoundError(f"Ticket {ticket_id} does not exist.")
            self._add_event(
                connection,
                ticket_id,
                "status_changed",
                f"Status changed to {status.value}.",
                changed_at,
            )
            row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return Ticket.from_row(row)

    def assign(self, ticket_id: int, assignee: str, changed_at: datetime) -> Ticket:
        with self.database.connect() as connection:
            cursor = connection.execute(
                "UPDATE tickets SET assignee = ? WHERE id = ?", (assignee, ticket_id)
            )
            if cursor.rowcount == 0:
                raise TicketNotFoundError(f"Ticket {ticket_id} does not exist.")
            self._add_event(connection, ticket_id, "assigned", f"Assigned to {assignee}.", changed_at)
            row = connection.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
        return Ticket.from_row(row)

    def events_for(self, ticket_id: int) -> list[TicketEvent]:
        self.get(ticket_id)
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ticket_events WHERE ticket_id = ? ORDER BY created_at ASC, id ASC",
                (ticket_id,),
            ).fetchall()
        return [TicketEvent.from_row(row) for row in rows]

    def open_tickets_for_sla(self) -> list[Ticket]:
        with self.database.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tickets WHERE status != ? ORDER BY due_at ASC, id ASC",
                (TicketStatus.RESOLVED.value,),
            ).fetchall()
        return [Ticket.from_row(row) for row in rows]

    def dashboard_metrics(self, now: datetime) -> dict[str, object]:
        with self.database.connect() as connection:
            totals = connection.execute(
                """
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN status != 'resolved' THEN 1 ELSE 0 END) AS open,
                    SUM(CASE WHEN status = 'resolved' THEN 1 ELSE 0 END) AS resolved,
                    SUM(CASE WHEN status != 'resolved' AND due_at < ? THEN 1 ELSE 0 END) AS overdue
                FROM tickets
                """,
                (now.isoformat(),),
            ).fetchone()
            status_rows = connection.execute(
                "SELECT status, COUNT(*) AS count FROM tickets GROUP BY status ORDER BY status"
            ).fetchall()
            team_rows = connection.execute(
                """
                SELECT team, COUNT(*) AS count FROM tickets
                WHERE status != 'resolved'
                GROUP BY team ORDER BY count DESC, team ASC
                """
            ).fetchall()
            category_rows = connection.execute(
                "SELECT category, COUNT(*) AS count FROM tickets GROUP BY category ORDER BY count DESC"
            ).fetchall()
            resolution_row = connection.execute(
                """
                SELECT AVG((julianday(resolved_at) - julianday(created_at)) * 24) AS hours
                FROM tickets
                WHERE resolved_at IS NOT NULL
                """
            ).fetchone()
        return {
            "total": totals["total"],
            "open": totals["open"] or 0,
            "resolved": totals["resolved"] or 0,
            "overdue": totals["overdue"] or 0,
            "by_status": {row["status"]: row["count"] for row in status_rows},
            "open_by_team": {row["team"]: row["count"] for row in team_rows},
            "by_category": {row["category"]: row["count"] for row in category_rows},
            "average_resolution_hours": round(resolution_row["hours"], 2)
            if resolution_row["hours"] is not None
            else None,
        }

    @staticmethod
    def _add_event(
        connection: object,
        ticket_id: int,
        event_type: str,
        detail: str,
        created_at: datetime,
    ) -> None:
        connection.execute(
            """
            INSERT INTO ticket_events (ticket_id, event_type, detail, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (ticket_id, event_type, detail, created_at.isoformat()),
        )
