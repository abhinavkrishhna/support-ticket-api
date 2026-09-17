# API examples

Run the app and open `http://127.0.0.1:8000/docs` to try the API in your browser.

## Create a ticket

`POST /tickets`

```json
{
  "title": "Nightly sales file is missing",
  "description": "The SFTP export did not arrive by 07:00.",
  "requester_email": "analyst@example.com"
}
```

The app returns the saved ticket. It also adds a category, team, priority, status, and due time.

## Check a team suggestion first

`POST /tickets/triage-preview`

```json
{
  "title": "I cannot sign in",
  "description": "My password was reset but the MFA code does not work."
}
```

The response includes the suggested category, team, priority, matching words, and a `match_score`. The score is the share of that category's keywords found in the ticket.

## Change a ticket status

`PATCH /tickets/1/status`

```json
{
  "status": "in_progress"
}
```

The allowed order is `new` to `in_progress` to `resolved`. If a user tries to skip a step, the app returns status code `409`.

## Useful links

| Method | URL | What it does |
| --- | --- | --- |
| `GET` | `/health` | Checks if the app is running. |
| `GET` | `/tickets` | Lists tickets. |
| `GET` | `/tickets/1` | Shows one ticket and its history. |
| `POST` | `/tickets/1/assign` | Assigns the ticket to a person. |
| `GET` | `/analytics/overview` | Shows ticket counts by status, team, and category. |
| `GET` | `/analytics/sla-queue` | Shows open tickets in due-time order. |
| `GET` | `/reports/daily` | Shows a daily summary. |
