# What this app needs to do

## The problem

A support team gets many messages every day. They need a simple way to record issues, decide who should handle them, and make sure urgent work is not forgotten.

## Users

- A requester creates a ticket.
- A support person checks and updates tickets.
- A team lead reads the report.

## Features

| Feature | What should happen |
| --- | --- |
| Create a ticket | A user gives a title, description, and email. The app saves it. |
| Suggest a team | The app checks the words in the ticket and suggests a team and priority. |
| Change the status | A ticket can move from `new` to `in_progress` to `resolved`. |
| Assign a person | A support person can assign a ticket to someone. |
| Keep history | The app saves creation, assignment, and status changes. |
| Show urgent work | The app lists open tickets by their due time. |
| Show a report | The app shows total, open, resolved, and overdue tickets. |
| Import a file | The app reads valid rows from a CSV file and skips bad rows. |
| Save daily reports | The app creates a CSV ticket list and a JSON summary file. |

## Things not included yet

This version does not have login, email alerts, file uploads, or a web page. Those would be good next steps after the backend is working well.
