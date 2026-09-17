from datetime import UTC, datetime, timedelta

from app.models import Ticket, TicketPriority, TicketStatus
from app.sla_queue import SlaQueue


def make_ticket(ticket_id: int, due_in_hours: int, priority: TicketPriority) -> Ticket:
    now = datetime(2026, 1, 1, tzinfo=UTC)
    return Ticket(
        id=ticket_id,
        title="Test ticket",
        description="A sufficiently detailed test description.",
        requester_email="test@example.com",
        category="access",
        team="identity-operations",
        priority=priority,
        status=TicketStatus.NEW,
        assignee=None,
        created_at=now,
        due_at=now + timedelta(hours=due_in_hours),
        resolved_at=None,
    )


def test_queue_returns_earliest_due_ticket_first() -> None:
    later = make_ticket(1, due_in_hours=24, priority=TicketPriority.URGENT)
    earlier = make_ticket(2, due_in_hours=4, priority=TicketPriority.LOW)

    queue = SlaQueue([later, earlier])

    assert [ticket.id for ticket in queue.next_items(2)] == [2, 1]


def test_queue_uses_priority_when_due_times_match() -> None:
    low = make_ticket(1, due_in_hours=12, priority=TicketPriority.LOW)
    urgent = make_ticket(2, due_in_hours=12, priority=TicketPriority.URGENT)

    assert SlaQueue([low, urgent]).next_items(1)[0].id == 2
