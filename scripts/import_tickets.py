"""Read tickets from a CSV file and save them in the database."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from pathlib import Path

from app.database import Database
from app.models import TicketPriority
from app.ticket_repository import TicketRepository
from app.ticket_service import TicketService


@dataclass
class ImportResult:
    added: int = 0
    skipped: int = 0
    errors: list[str] = field(default_factory=list)


def import_tickets(csv_file: Path, service: TicketService) -> ImportResult:
    result = ImportResult()
    with csv_file.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        needed_columns = {"title", "description", "requester_email"}
        if not reader.fieldnames or not needed_columns.issubset(reader.fieldnames):
            raise ValueError("CSV file must have title, description, and requester_email columns.")

        for row_number, row in enumerate(reader, start=2):
            try:
                title = str(row.get("title") or "").strip()
                description = str(row.get("description") or "").strip()
                email = str(row.get("requester_email") or "").strip()
                if not title or not description or "@" not in email:
                    raise ValueError("title, description, and a valid email are required")

                priority_text = str(row.get("priority") or "").strip().lower()
                priority = TicketPriority(priority_text) if priority_text else None
                team = str(row.get("team") or "").strip() or None
                urgent = str(row.get("urgent") or "").strip().lower() in {"true", "yes", "1"}
                service.create_ticket(
                    title=title,
                    description=description,
                    requester_email=email,
                    priority=priority,
                    team=team,
                    urgent=urgent,
                )
                result.added += 1
            except (KeyError, ValueError) as error:
                result.skipped += 1
                result.errors.append(f"Row {row_number}: {error}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Import support tickets from a CSV file.")
    parser.add_argument("file", type=Path)
    parser.add_argument("--database", default="data/support_tickets.db")
    args = parser.parse_args()

    database = Database(args.database)
    database.initialize()
    result = import_tickets(args.file, TicketService(TicketRepository(database)))
    print(f"Added: {result.added}")
    print(f"Skipped: {result.skipped}")
    for error in result.errors:
        print(error)


if __name__ == "__main__":
    main()
