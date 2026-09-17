# Git, testing, and simple project process

## Git

The project is already a Git repository. Make a new branch for each change.

```powershell
git checkout -b add-email-alerts
git add .
git commit -m "Add email alerts"
git push -u origin add-email-alerts
```

Use short commit messages that say what changed. Examples are `Add ticket search`, `Fix SLA queue order`, and `Update API notes`.

## Testing

The `tests` folder checks the important parts of the app.

| Test file | What it checks |
| --- | --- |
| `test_triage.py` | Team suggestion from ticket words. |
| `test_sla.py` | Tickets are ordered by their due time and priority. |
| `test_ticket_workflow.py` | Status rules, ticket history, and overview numbers. |
| `test_api.py` | The API can create a ticket and return overview data. |
| `test_import_tickets.py` | A CSV file adds valid rows and skips bad rows. |
| `test_report_writer.py` | A daily report creates CSV and JSON files. |

Run the checks before you push code:

```powershell
pytest -q
ruff check .
```

## GitHub Actions

The file `.github/workflows/ci.yml` runs the same checks on GitHub after you push your code. A green tick means the checks passed.

## Simple way to build features

1. Write down what the feature should do.
2. Change the smallest amount of code needed.
3. Add or update a test.
4. Run the tests.
5. Update the README or API notes if needed.
6. Commit and push the change.
