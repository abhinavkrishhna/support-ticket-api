# Batch jobs

The app has two commands that can run without starting FastAPI.

## Import tickets from a CSV file

Run this command from the project folder:

```powershell
python -m scripts.import_tickets sample_data/tickets.csv
```

The import reads one row at a time. It saves rows with a title, description, and email. If a row is missing required data or has an invalid priority, the command skips it and prints the row number.

This is useful when a support team receives tickets from a spreadsheet or another system.

## Create the daily report

Run this command from the project folder:

```powershell
python -m scripts.daily_report
```

It creates a CSV file with the ticket details and a JSON file with the summary numbers. The files go in the `reports` folder by default.

You can use a different database or output folder:

```powershell
python -m scripts.daily_report --database data/support_tickets.db --output-folder reports
```

## Run it every day in Windows Task Scheduler

1. Open Task Scheduler and choose Create Basic Task.
2. Give it a name such as `Support Ticket Daily Report`.
3. Choose Daily and select the time you want.
4. Choose Start a program.
5. Select your Python executable, for example `C:\Python311\python.exe`.
6. In Add arguments, enter `-m scripts.daily_report`.
7. In Start in, enter the full path to the `support-ticket-app` folder.
8. Finish the task and use Run once to check that the report files appear.

This is an unattended job. It reads the database and creates a new report each day without someone opening the API or copying data by hand.
