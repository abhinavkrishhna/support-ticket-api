"""The main ticket objects used by the app."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class TicketStatus(str, Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


@dataclass(frozen=True, slots=True)
class Ticket:
    """One support ticket."""

    id: int
    title: str
    description: str
    requester_email: str
    category: str
    team: str
    priority: TicketPriority
    status: TicketStatus
    assignee: str | None
    created_at: datetime
    due_at: datetime
    resolved_at: datetime | None

    @property
    def is_open(self) -> bool:
        return self.status is not TicketStatus.RESOLVED

    @classmethod
    def from_row(cls, row: Any) -> Ticket:
        """Make a Ticket object from a database row."""
        return cls(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            requester_email=row["requester_email"],
            category=row["category"],
            team=row["team"],
            priority=TicketPriority(row["priority"]),
            status=TicketStatus(row["status"]),
            assignee=row["assignee"],
            created_at=datetime.fromisoformat(row["created_at"]),
            due_at=datetime.fromisoformat(row["due_at"]),
            resolved_at=(datetime.fromisoformat(row["resolved_at"]) if row["resolved_at"] else None),
        )


@dataclass(frozen=True, slots=True)
class TriageResult:
    category: str
    team: str
    priority: TicketPriority
    match_score: float
    matched_terms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TicketEvent:
    id: int
    ticket_id: int
    event_type: str
    detail: str
    created_at: datetime

    @classmethod
    def from_row(cls, row: Any) -> TicketEvent:
        return cls(
            id=row["id"],
            ticket_id=row["ticket_id"],
            event_type=row["event_type"],
            detail=row["detail"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
