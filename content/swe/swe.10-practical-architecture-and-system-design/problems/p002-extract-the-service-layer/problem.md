# Extract the service layer

Chapter sections 4.1 to 4.3 (the service layer, rules for a good service function, the thin route) and 2.2 (the first version). In the first version of Taskboard the whole use case "create a task" lives inside the web handler: HTTP, rules, SQL, audit and e-mail in one block. That is the first pain: another caller (a command-line import) cannot use the rules, and each handler is its own island.

```python
# the route today (taskboard/main.py, chapter 2.2)
@app.post("/projects/{project_id}/tasks", status_code=201)
def create_task(project_id: int, body: NewTask):
    conn = db.get_conn()
    title = body.title.strip()
    if not title or len(title) > 120:
        raise HTTPException(422, "title must have 1 to 120 characters")
    if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
        raise HTTPException(404, "project not found")
    if body.assignee_id is not None:
        member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                              (project_id, body.assignee_id)).fetchone()
        if member is None:
            raise HTTPException(409, "assignee is not a member of this project")
        open_count = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'",
                                  (body.assignee_id,)).fetchone()[0]
        if open_count >= MAX_OPEN:
            raise HTTPException(409, f"assignee already has {MAX_OPEN} open tasks")
    stamp = now()
    cur = conn.execute("INSERT INTO tasks (project_id, title, status, assignee_id, created_at) VALUES (?, ?, 'todo', ?, ?)",
                       (project_id, title, body.assignee_id, stamp))
    task_id = cur.lastrowid
    conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'created', ?)", (task_id, stamp))
    if body.assignee_id is not None:
        email = conn.execute("SELECT email FROM users WHERE id = ?", (body.assignee_id,)).fetchone()[0]
        mailer.send_email(email, f"New task: {title}")
    conn.commit()
    return {"id": task_id, "title": title, "status": "todo", "assignee_id": body.assignee_id}
```

## What to write

In `solution.py` the **route is already thin** (it opens a connection, calls your function, commits or rolls back, and maps domain errors to HTTP in `create_app`). You write the **service function**, the same rules without any HTTP:

```python
def create_task(conn, mailer, project_id, title, assignee_id=None) -> dict: ...
```

Rules of a good service function (chapter 4.2):

- **No HTTP knowledge.** It never raises `HTTPException` and never mentions a status code. It raises the domain errors given in the starter: `InvalidInput` for a bad title, `NotFound` for an unknown project, `RuleViolation` for "not a member" and for "already has 3 open tasks" (the message contains `3 open tasks`).
- Rules, in this order: the title (trimmed, 1 to 120 characters) is checked **first**; then the project; then, if there is an assignee, membership and then capacity (`MAX_OPEN = 3` tasks with a status other than `done`).
- It inserts the task (`status 'todo'`, `created_at` = any ISO time string), writes the audit line `'created'`, and, if there is an assignee, sends one e-mail with `mailer.send_email(address, f"New task: {title}")` (the address is that user's `email`).
- It returns `{"id": ..., "title": <trimmed title>, "status": "todo", "assignee_id": ...}`.
- **It does not commit.** The caller decides when the transaction ends (the route commits after success and rolls back on any exception).

## Example

```python
conn = <a sqlite3 connection with the Taskboard schema>
create_task(conn, mailer, 1, "  Write docs  ", assignee_id=1)
# {'id': 1, 'title': 'Write docs', 'status': 'todo', 'assignee_id': 1}     (and mailer.sent == [('ana@example.com', 'New task: Write docs')])
create_task(conn, mailer, 1, "x", assignee_id=3)     # RuleViolation: user 3 is not a member of project 1
```

The tests call your function directly, with no FastAPI, and also drive the finished app over HTTP to prove that the outside did not change.
