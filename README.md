# TimelineToGantt

This tool retrieves a notion database and converts it into a usable gantt chart. This means we can use notion timeline veiw interally, but have an easy way to export it for external reports.

## How does it work

Once given a notion api key and the page is where the database is contained, it will retives all the tasks in the database.
If a tasks in the database has a date, it will covert the item into a Task object. These objects are sepearted by the type of task (rocket parts, orgainsation, due dates, etc). All tasks are then coverted into mermaid code, which generates the gantt chart. The code is uploaded back to notion where the gantt chart can be veiwed.
