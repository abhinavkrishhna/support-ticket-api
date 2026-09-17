"""Rules for creating and updating tickets."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.models import Ticket, TicketPriority, TicketStatus, TriageResult
from app.sla_queue import SlaQueue
from app.ticket_repository import TicketRepository
from app.triage import TicketClassifier


class InvalidStatusChangeError(ValueError):
    """A ticket was given a status it cannot move to."""


SLA_HOURS = {
    TicketPriority.URGENT: 4,
    TicketPriority.HIGH: 12,
    TicketPriority.MEDIUM: 24,
    TicketPriority.LOW: 72,
}

ALLOWED_TRANSITIONS = {
    TicketStatus.NEW: {TicketStatus.IN_PROGRESS},
    TicketStatus.IN_PROGRESS: {TicketStatus.RESOLVED},
    TicketStatus.RESOLVED: set(),
}


class TicketService:
    def __init__(
        self, repository: TicketRepository, classifier: TicketClassifier | None = None
    ) -> None:
        self.repository = repository
        self.classifier = classifier or TicketClassifier()

    def preview_triage(self, title: str, description: str, urgent: bool = False) -> TriageResult:
        return self.classifier.suggest(f"{title} {description}", urgent)

    def create_ticket(
        self,
        *,
        title: str,
        description: str,
        requester_email: str,
        priority: TicketPriority | None = None,
        team: str | None = None,
        urgent: bool = False,
        now: datetime | None = None,
    ) -> Ticket:
        now = now or datetime.now(UTC)
        recommendation = self.preview_triage(title, description, urgent)
        selected_priority = priority or recommendation.priority
        selected_team = team or recommendation.team
        due_at = now + timedelta(hours=SLA_HOURS[selected_priority])
        return self.repository.create(
            title=title,
            description=description,
            requester_email=requester_email,
            category=recommendation.category,
            team=selected_team,
            priority=selected_priority,
            created_at=now,
            due_at=due_at,
        )

    def change_status(
        self, ticket_id: int, target_status: TicketStatus, now: datetime | None = None
    ) -> Ticket:
        ticket = self.repository.get(ticket_id)
        if target_status not in ALLOWED_TRANSITIONS[ticket.status]:
            raise InvalidStatusChangeError(
                f"Cannot change ticket {ticket_id} from {ticket.status.value} to {target_status.value}."
            )
        return self.repository.update_status(ticket_id, target_status, now or datetime.now(UTC))

    def assign(self, ticket_id: int, assignee: str, now: datetime | None = None) -> Ticket:
        return self.repository.assign(ticket_id, assignee, now or datetime.now(UTC))

    def sla_queue(self, limit: int = 10) -> list[Ticket]:
        open_tickets = self.repository.open_tickets_for_sla()
        return SlaQueue(open_tickets).next_items(limit)

    def overview(self, now: datetime | None = None) -> dict[str, object]:
        return self.repository.dashboard_metrics(now or datetime.now(UTC))

    def daily_report(self, now: datetime | None = None) -> dict[str, object]:
        current_time = now or datetime.now(UTC)
        metrics = self.overview(current_time)
        return {
            "report_generated_at": current_time,
            "headline": (
                f"{metrics['open']} open tickets; {metrics['overdue']} past SLA; "
                f"{metrics['resolved']} resolved."
            ),
            "metrics": metrics,
            "next_up": self.sla_queue(limit=5),
        }
