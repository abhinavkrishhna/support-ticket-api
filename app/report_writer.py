"""Create files that a support lead can open and share."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from app.models import Ticket
from app.ticket_repository import TicketRepository


@dataclass(frozen=True, slots=True)
class ReportFiles:
    csv_file: Path
    summary_file: Path


class ReportWriter:
    def __init__(self, repository: TicketRepository) -> None:
        self.repository = repository

    def write_daily_report(
        self, output_folder: Path, now: datetime | None = None
    ) -> ReportFiles:
        report_time = now or datetime.now(UTC)
        output_folder.mkdir(parents=True, exist_ok=True)
        report_date = report_time.date().isoformat()
        csv_file = output_folder / f"ticket_report_{report_date}.csv"
        summary_file = output_folder / f"ticket_summary_{report_date}.json"
        tickets = self.repository.list(limit=500)
        metrics = self.repository.dashboard_metrics(report_time)

        self._write_csv(csv_file, tickets, report_time)
        self._write_summary(summary_file, metrics, report_time)
        return ReportFiles(csv_file=csv_file, summary_file=summary_file)

    @staticmethod
    def _write_csv(csv_file: Path, tickets: list[Ticket], report_time: datetime) -> None:
        with csv_file.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "ticket_id",
                    "title",
                    "category",
                    "team",
                    "priority",
                    "status",
                    "assignee",
                    "created_at",
                    "due_at",
                    "resolved_at",
                    "is_overdue",
                ],
            )
            writer.writeheader()
            for ticket in tickets:
                writer.writerow(
                    {
                        "ticket_id": ticket.id,
                        "title": ticket.title,
                        "category": ticket.category,
                        "team": ticket.team,
                        "priority": ticket.priority.value,
                        "status": ticket.status.value,
                        "assignee": ticket.assignee or "",
                        "created_at": ticket.created_at.isoformat(),
                        "due_at": ticket.due_at.isoformat(),
                        "resolved_at": ticket.resolved_at.isoformat() if ticket.resolved_at else "",
                        "is_overdue": ticket.is_open and ticket.due_at < report_time,
                    }
                )

    @staticmethod
    def _write_summary(summary_file: Path, metrics: dict[str, object], report_time: datetime) -> None:
        summary = {"created_at": report_time.isoformat(), **metrics}
        summary_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")
