"""Make daily report files from the ticket database."""

from __future__ import annotations

import argparse
from pathlib import Path

from app.database import Database
from app.report_writer import ReportWriter
from app.ticket_repository import TicketRepository


def make_report(database_path: str, output_folder: Path) -> tuple[Path, Path]:
    database = Database(database_path)
    database.initialize()
    writer = ReportWriter(TicketRepository(database))
    files = writer.write_daily_report(output_folder)
    return files.csv_file, files.summary_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Create the daily support ticket report.")
    parser.add_argument("--database", default="data/support_tickets.db")
    parser.add_argument("--output-folder", default="reports")
    args = parser.parse_args()

    csv_file, summary_file = make_report(args.database, Path(args.output_folder))
    print(f"Created {csv_file}")
    print(f"Created {summary_file}")


if __name__ == "__main__":
    main()
