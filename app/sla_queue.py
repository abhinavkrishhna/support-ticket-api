"""A small queue that puts urgent work first."""

from __future__ import annotations

import heapq
from dataclasses import dataclass, field
from datetime import datetime

from app.models import Ticket, TicketPriority

PRIORITY_WEIGHT = {
    TicketPriority.URGENT: 0,
    TicketPriority.HIGH: 1,
    TicketPriority.MEDIUM: 2,
    TicketPriority.LOW: 3,
}


@dataclass(order=True)
class QueueItem:
    due_at: datetime
    priority_weight: int
    ticket_id: int
    ticket: Ticket = field(compare=False)


class SlaQueue:
    """Sort open tickets by their SLA due time."""

    def __init__(self, tickets: list[Ticket] | None = None) -> None:
        self._heap: list[QueueItem] = []
        for ticket in tickets or []:
            self.add(ticket)

    def add(self, ticket: Ticket) -> None:
        if ticket.is_open:
            heapq.heappush(
                self._heap,
                QueueItem(ticket.due_at, PRIORITY_WEIGHT[ticket.priority], ticket.id, ticket),
            )

    def next_items(self, limit: int) -> list[Ticket]:
        heap_copy = list(self._heap)
        heapq.heapify(heap_copy)
        return [heapq.heappop(heap_copy).ticket for _ in range(min(limit, len(heap_copy)))]
