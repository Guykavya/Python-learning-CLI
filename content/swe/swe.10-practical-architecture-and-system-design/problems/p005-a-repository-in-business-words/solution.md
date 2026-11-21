## Approach

```python
class SqliteTaskRepo:
    def __init__(self, conn):
        self.conn = conn

    def add(self, task):
        cur = self.conn.execute("INSERT INTO tasks (project_id, title, status, assignee_id, created_at, completed_at) VALUES (?, ?, ?, ?, ?, ?)", (...))
        task.id = cur.lastrowid
        return task

    def get(self, task_id):
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            raise NotFound(f"task {task_id} not found")
        return _task(row)
    ...
```

The method names are the **business words** (`open_count_for`, `list_for_project`), not table words (`select_tasks_where_assignee`). A service that uses this class has no `SELECT` in it, so it reads like the rules of section 2.1. **All SQL of the program is now in one file** (chapter 5.2): when the storage changes (an index, a new column, another database), this is the only class to touch.

## Cost

About 90 lines for the three repositories in the chapter, plus the mapping function. The chapter is honest (6.4): the repository is a bill (a new file, a mapping, one more jump when reading) and it pays when rules and SQL are tangled or tests need a database. For a one-table app with no rules, skip it.

## Another way

SQLAlchemy's `Session` is already a repository-and-unit-of-work (chapter 7.4): if you use it, wrap it only where you need fakes or want to stop ORM details leaking into the rules.
