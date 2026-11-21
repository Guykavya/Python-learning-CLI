from datetime import datetime, timezone

MAX_OPEN = 3
ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}
SENT = []                                  # (address, subject) of every e-mail "sent"


class DomainError(Exception):
    pass


class NotFound(DomainError):
    pass


class InvalidInput(DomainError):
    pass


class RuleViolation(DomainError):
    pass


def send_email(to, subject):
    SENT.append((to, subject))


def _now():
    return datetime.now(timezone.utc).isoformat()


def _check_member(conn, project_id, user_id):
    row = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?", (project_id, user_id)).fetchone()
    if row is None:
        raise RuleViolation("assignee is not a member of this project")


def _check_capacity(conn, user_id):
    """Rule 3, written exactly once."""
    n = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'", (user_id,)).fetchone()[0]
    if n >= MAX_OPEN:
        raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")


def create_task(conn, project_id, title, assignee_id=None):
    title = title.strip()
    if not title or len(title) > 120:
        raise InvalidInput("title must have 1 to 120 characters")
    if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
        raise NotFound("project not found")
    if assignee_id is not None:
        _check_member(conn, project_id, assignee_id)
        _check_capacity(conn, assignee_id)
    stamp = _now()
    cur = conn.execute("INSERT INTO tasks (project_id, title, status, assignee_id, created_at) VALUES (?, ?, 'todo', ?, ?)",
                       (project_id, title, assignee_id, stamp))
    task_id = cur.lastrowid
    conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'created', ?)", (task_id, stamp))
    if assignee_id is not None:
        email = conn.execute("SELECT email FROM users WHERE id = ?", (assignee_id,)).fetchone()[0]
        send_email(email, f"New task: {title}")
    return _task_json(conn, task_id)


def update_task(conn, task_id, assignee_id=None, status=None):
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        raise NotFound("task not found")
    stamp = _now()
    current_status, current_assignee = task["status"], task["assignee_id"]
    if assignee_id is not None:
        _check_member(conn, task["project_id"], assignee_id)
        if current_status != "done" and assignee_id != current_assignee:
            _check_capacity(conn, assignee_id)                         # an open task moving to a new person
        conn.execute("UPDATE tasks SET assignee_id = ? WHERE id = ?", (assignee_id, task_id))
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'assigned', ?)", (task_id, stamp))
        email = conn.execute("SELECT email FROM users WHERE id = ?", (assignee_id,)).fetchone()[0]
        send_email(email, f"Task assigned: {task['title']}")
        current_assignee = assignee_id
    if status is not None:
        if (current_status, status) not in ALLOWED:
            raise RuleViolation(f"cannot move from {current_status} to {status}")
        if current_status == "done" and current_assignee is not None:
            _check_capacity(conn, current_assignee)                    # reopening makes the task open again
        completed = stamp if status == "done" else None
        conn.execute("UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?", (status, completed, task_id))
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, ?, ?)", (task_id, f"status:{status}", stamp))
    return _task_json(conn, task_id)


def _task_json(conn, task_id):
    t = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return {"id": t["id"], "project_id": t["project_id"], "title": t["title"], "status": t["status"],
            "assignee_id": t["assignee_id"], "completed_at": t["completed_at"]}
