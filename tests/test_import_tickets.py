from app.database import Database
from app.ticket_repository import TicketRepository
from app.ticket_service import TicketService
from scripts.import_tickets import import_tickets


def test_import_tickets_adds_valid_rows_and_reports_bad_rows(tmp_path) -> None:
    csv_file = tmp_path / "tickets.csv"
    csv_file.write_text(
        "title,description,requester_email,priority\n"
        "Missing sales file,The SFTP export did not arrive.,analyst@example.com,high\n"
        "Bad ticket,Missing email address,,medium\n",
        encoding="utf-8",
    )
    database = Database(str(tmp_path / "support_tickets.db"))
    database.initialize()
    service = TicketService(TicketRepository(database))

    result = import_tickets(csv_file, service)

    assert result.added == 1
    assert result.skipped == 1
    assert "Row 3" in result.errors[0]
    assert len(service.repository.list()) == 1
