import csv
import json
from datetime import UTC, datetime

from app.database import Database
from app.report_writer import ReportWriter
from app.ticket_repository import TicketRepository
from app.ticket_service import TicketService


def test_report_writer_creates_csv_and_json_files(tmp_path) -> None:
    database = Database(str(tmp_path / "support_tickets.db"))
    database.initialize()
    repository = TicketRepository(database)
    service = TicketService(repository)
    report_time = datetime(2026, 1, 1, 9, tzinfo=UTC)
    service.create_ticket(
        title="Sales file is missing",
        description="The SFTP file did not arrive for the dashboard.",
        requester_email="analyst@example.com",
        now=report_time,
    )

    files = ReportWriter(repository).write_daily_report(tmp_path / "reports", now=report_time)

    with files.csv_file.open(newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))
    summary = json.loads(files.summary_file.read_text(encoding="utf-8"))

    assert len(rows) == 1
    assert rows[0]["team"] == "data-operations"
    assert rows[0]["is_overdue"] == "False"
    assert summary["total"] == 1
    assert summary["by_category"] == {"data_pipeline": 1}
