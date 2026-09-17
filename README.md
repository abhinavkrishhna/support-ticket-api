# Support Ticket App

A small FastAPI and SQLite app for a support team. It records tickets, suggests a team from the ticket text, tracks the ticket status, and creates daily report files.

## What it does

- Creates support tickets through REST API endpoints.
- Suggests a team and priority from keywords in the ticket.
- Tracks tickets from `new` to `in_progress` to `resolved`.
- Keeps a history of ticket changes in the database.
- Shows open work in SLA due-time order.
- Imports many tickets from a CSV file.
- Creates a CSV ticket report and JSON summary file.

## Tech used

- Python and FastAPI for the API
- SQLite and SQL for storage and reports
- `heapq` for the SLA queue
- `csv` and `json` from Python for batch data work
- Pytest and Ruff for checks
- GitHub Actions for the same checks on GitHub

SQLite is a good fit for this local project. For a production system with many people writing tickets at the same time, I would use PostgreSQL.

## Project folders

```text
support-ticket-app/
|
|-- app/                 API code, database code, and ticket rules
|-- scripts/             commands for importing data and making reports
|-- sample_data/         example CSV file for the import command
|-- tests/               automated tests
|-- docs/                short notes about the project
|-- requirements.txt     Python packages
`-- Dockerfile           optional Docker setup
```

## Run the API

You need Python 3.11 or newer.

```powershell
git clone <your-github-repository-url>
cd support-ticket-app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to try the API in your browser.

## Quick example

```powershell
$ticket = @{
  title = "Nightly sales file is missing"
  description = "The SFTP export did not arrive by 07:00."
  requester_email = "analyst@example.com"
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/tickets" `
  -ContentType "application/json" `
  -Body $ticket
```

Useful API URLs:

```text
http://127.0.0.1:8000/analytics/overview
http://127.0.0.1:8000/analytics/sla-queue
http://127.0.0.1:8000/reports/daily
```

## Batch work

### Import a CSV file

This command reads each row in a CSV file, adds valid tickets to the database, and prints rows that were skipped.

```powershell
python -m scripts.import_tickets sample_data/tickets.csv
```

The sample file has these columns:

```text
title,description,requester_email,priority,team,urgent
```

### Create a daily report

This command creates two files in the `reports` folder:

- `ticket_report_YYYY-MM-DD.csv` has one row for every ticket.
- `ticket_summary_YYYY-MM-DD.json` has ticket counts, team counts, category counts, overdue count, and average resolution time.

```powershell
python -m scripts.daily_report
```

The report command can run by itself. It can be added to Windows Task Scheduler to create the report every morning. See [Automation notes](docs/AUTOMATION.md).

## Main files

| File | What it does |
| --- | --- |
| `app/main.py` | API routes |
| `app/models.py` | Ticket data, status, and priority |
| `app/ticket_service.py` | Ticket rules and SLA time calculation |
| `app/ticket_repository.py` | SQL queries |
| `app/triage.py` | Keyword matching for team suggestions |
| `app/sla_queue.py` | Heap queue for nearest due ticket |
| `app/report_writer.py` | Creates report files |
| `scripts/import_tickets.py` | Imports ticket data from CSV |
| `scripts/daily_report.py` | Runs the daily report job |

## Run checks

```powershell
pytest -q
ruff check .
```

## Notes

- [Requirements](docs/REQUIREMENTS.md)
- [Code layout](docs/ARCHITECTURE.md)
- [API examples](docs/API.md)
- [Batch jobs](docs/AUTOMATION.md)
- [Git and tests](docs/SDLC.md)
