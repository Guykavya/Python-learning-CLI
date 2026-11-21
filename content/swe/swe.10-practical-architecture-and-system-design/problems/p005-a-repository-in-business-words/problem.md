# A repository in business words

Chapter sections 5.1 to 5.3 (the repository: design the interface in business words). After the service layer (p002) there is still SQL inside the rule code, which makes rules hard to read and tests need a real database. A **repository** hides how tasks are stored: the service asks questions in the words of the business, and gets a `Task` object, not a database row.

## What to write

`Task` (a dataclass) and the errors are given. Write `SqliteTaskRepo(conn)` for the Taskboard schema (`tasks` table; see the chapter's schema in section 2.2):

```python
class SqliteTaskRepo:
    def __init__(self, conn): ...
    def add(self, task) -> Task: ...                              # insert; sets task.id; returns the same task
    def get(self, task_id) -> Task: ...                           # a NEW Task each time; raises NotFound if there is none
    def save(self, task) -> None: ...                             # store the changes of title, status, assignee_id, completed_at
    def open_count_for(self, user_id) -> int: ...                 # tasks of that user whose status is not 'done'
    def list_for_project(self, project_id, status=None) -> list[Task]: ...   # ordered by id; optionally only that status
```

Rules:

- **All SQL lives in this class.** Returning `Task` objects (never `sqlite3.Row`) is what lets the rest of the program forget SQL.
- `get` raises `NotFound` (with a message naming the id) for an unknown id: the business word for "there is no such task" is an error, not `None`.
- `add` and `save` **do not commit**: the caller owns the transaction (chapter 7).
- `open_count_for` counts only that user's tasks that are not `done`; tasks of other users and unassigned tasks are ignored.
- `conn` has `row_factory = sqlite3.Row`.

## Example

```python
repo = SqliteTaskRepo(conn)
t = repo.add(Task(None, 1, "Write docs", "todo", 1, "2026-01-01T00:00:00"))
t.id                              # 1
repo.get(1) == t                  # True (equal data, but a different object)
repo.open_count_for(1)            # 1
repo.get(99)                      # NotFound
```
