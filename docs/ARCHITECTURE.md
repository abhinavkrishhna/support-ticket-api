# How the code is organised

The app is split into small files so it is easier to understand.

| File | Job |
| --- | --- |
| `main.py` | Receives API requests and sends responses. |
| `api_models.py` | Checks the data sent to the API. |
| `models.py` | Holds the Ticket, status, priority, and history objects. |
| `ticket_service.py` | Contains rules, such as which status changes are allowed. |
| `ticket_repository.py` | Contains the SQL queries. |
| `database.py` | Creates the database tables. |
| `triage.py` | Matches ticket words with a team. |
| `sla_queue.py` | Orders open tickets by their due time. |
| `report_writer.py` | Creates the CSV and JSON report files. |
| `scripts/import_tickets.py` | Reads ticket rows from a CSV file. |
| `scripts/daily_report.py` | Runs the report task without the API server. |

## Database tables

The `tickets` table stores the current ticket details.

The `ticket_events` table stores the changes made to a ticket. For example, it records when the ticket was created, assigned, or resolved.

SQLite foreign key checks are turned on, so an event cannot be saved for a ticket that does not exist.

## How the queue works

The app uses a heap queue from Python's `heapq` module. The ticket with the nearest due time stays at the top of the queue. If two tickets have the same due time, the one with the higher priority comes first.

## How the team suggestion works

The app has a small list of keywords for each type of ticket.

- `password`, `login`, and `mfa` suggest the identity team.
- `file`, `sftp`, and `etl` suggest the data team.
- `api`, `server`, and `error` suggest the application support team.
- `invoice` and `payment` suggest the finance team.

This is simple and easy to explain. A bigger version could use real, approved ticket data to train a machine learning model.

If no keywords match, the app sends the ticket to `general` and the `support-desk` team instead of guessing a category.

## Basic safety choices

The API checks the input before saving it. The SQL uses `?` placeholders for values instead of putting user input directly into a query.
