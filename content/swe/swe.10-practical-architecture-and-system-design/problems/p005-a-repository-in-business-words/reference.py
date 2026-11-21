from dataclasses import dataclass


class DomainError(Exception):
    pass


class NotFound(DomainError):
    pass


@dataclass
class Task:
    id: int | None
    project_id: int
    title: str
    status: str
    assignee_id: int | None
    created_at: str
    completed_at: str | None = None


def _task(row):
    return Task(id=row["id"], project_id=row["project_id"], title=row["title"], status=row["status"],
                assignee_id=row["assignee_id"], created_at=row["created_at"], completed_at=row["completed_at"])


class SqliteTaskRepo:
    def __init__(self, conn):
        self.conn = conn

    def add(self, task):
        cur = self.conn.execute(
            "INSERT INTO tasks (project_id, title, status, assignee_id, created_at, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
            (task.project_id, task.title, task.status, task.assignee_id, task.created_at, task.completed_at))
        task.id = cur.lastrowid
        return task

    def get(self, task_id):
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise NotFound(f"task {task_id} not found")
        return _task(row)

    def save(self, task):
        self.conn.execute("UPDATE tasks SET title = ?, status = ?, assignee_id = ?, completed_at = ? WHERE id = ?",
                          (task.title, task.status, task.assignee_id, task.completed_at, task.id))

    def open_count_for(self, user_id):
        return self.conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'", (user_id,)).fetchone()[0]

    def list_for_project(self, project_id, status=None):
        sql, args = "SELECT * FROM tasks WHERE project_id = ?", [project_id]
        if status is not None:
            sql, args = sql + " AND status = ?", args + [status]
        return [_task(r) for r in self.conn.execute(sql + " ORDER BY id", args).fetchall()]
