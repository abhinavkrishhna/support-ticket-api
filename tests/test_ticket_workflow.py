from datetime import UTC, datetime, timedelta

import pytest

from app.database import Database
from app.models import TicketStatus
from app.ticket_repository import TicketRepository
from app.ticket_service import InvalidStatusChangeError, TicketService


@pytest.fixture
def service(tmp_path) -> TicketService:
    database = Database(str(tmp_path / "test-support-tickets.db"))
    database.initialize()
    return TicketService(TicketRepository(database))


def test_ticket_status_rules_and_history(service: TicketService) -> None:
    now = datetime(2026, 1, 1, 9, tzinfo=UTC)
    ticket = service.create_ticket(
        title="The nightly SFTP sales file is missing",
        description="No export arrived and dashboard records are stale.",
        requester_email="analyst@example.com",
        now=now,
    )

    assert ticket.category == "data_pipeline"
    assert ticket.due_at == now + timedelta(hours=12)
    assert ticket.status is TicketStatus.NEW
    assert len(service.repository.events_for(ticket.id)) == 1

    with pytest.raises(InvalidStatusChangeError):
        service.change_status(ticket.id, TicketStatus.RESOLVED, now=now)

    service.assign(ticket.id, "devika.rao", now=now)
    in_progress = service.change_status(ticket.id, TicketStatus.IN_PROGRESS, now=now)
    resolved = service.change_status(ticket.id, TicketStatus.RESOLVED, now=now)

    assert in_progress.status is TicketStatus.IN_PROGRESS
    assert resolved.resolved_at == now
    assert [event.event_type for event in service.repository.events_for(ticket.id)] == [
        "created",
        "assigned",
        "status_changed",
        "status_changed",
    ]


def test_overview_counts_open_and_overdue_work(service: TicketService) -> None:
    start = datetime(2026, 1, 1, 9, tzinfo=UTC)
    service.create_ticket(
        title="I cannot sign in after password reset",
        description="The login screen rejects my valid MFA code.",
        requester_email="user@example.com",
        now=start,
    )

    metrics = service.overview(now=start + timedelta(hours=13))

    assert metrics["total"] == 1
    assert metrics["open"] == 1
    assert metrics["overdue"] == 1
    assert metrics["open_by_team"] == {"identity-operations": 1}


def test_overview_shows_category_and_average_resolution_time(service: TicketService) -> None:
    start = datetime(2026, 1, 1, 9, tzinfo=UTC)
    ticket = service.create_ticket(
        title="The SFTP file is missing",
        description="The data export did not arrive for the dashboard.",
        requester_email="analyst@example.com",
        now=start,
    )
    service.change_status(ticket.id, TicketStatus.IN_PROGRESS, now=start + timedelta(hours=1))
    service.change_status(ticket.id, TicketStatus.RESOLVED, now=start + timedelta(hours=5))

    metrics = service.overview(now=start + timedelta(hours=5))

    assert metrics["by_category"] == {"data_pipeline": 1}
    assert metrics["average_resolution_hours"] == 5.0
