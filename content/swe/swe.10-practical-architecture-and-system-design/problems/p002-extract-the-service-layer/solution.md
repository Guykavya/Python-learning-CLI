## Approach

```python
def create_task(conn, mailer, project_id, title, assignee_id=None):
    title = title.strip()
    if not title or len(title) > 120:
        raise InvalidInput("title must have 1 to 120 characters")
    if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
        raise NotFound("project not found")
    if assignee_id is not None:
        member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?", (project_id, assignee_id)).fetchone()
        if member is None:
            raise RuleViolation("assignee is not a member of this project")
        open_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'", (assignee_id,)).fetchone()[0]
        if open_count >= MAX_OPEN:
            raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")
    ...insert the task and the audit line, send the e-mail...
    return {"id": task_id, "title": title, "status": "todo", "assignee_id": assignee_id}
```

The route shrinks to a translator (given in the starter): read the request, call one service function, commit or roll back, and turn domain errors into HTTP codes in **one** place. What this bought (chapter 4.4): a second caller, such as a command-line bulk import, can call `create_task` and get exactly the same rules, with no web server; and a rule changes in one place (chapter "Try it: add a rule in one place").

## Cost

The same SQL and the same rules as before, in a different place, plus a few lines of translation. Still SQL inside the service (the repository, p005, removes that) and still a connection passed in by hand (the unit of work, p009).

## Another way

A service class (`TaskService(conn)`) works too, as long as it stays a set of small use cases. The chapter warns against a "god service" with 40 methods and against services that return `Response` objects or raise `HTTPException`: that glues them back to the web.
