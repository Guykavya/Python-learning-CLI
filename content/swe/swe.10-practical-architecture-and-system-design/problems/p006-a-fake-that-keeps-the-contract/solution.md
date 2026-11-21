## Approach

```python
class FakeTaskRepo:
    def __init__(self):
        self.tasks, self.next_id = {}, 1

    def add(self, task):
        task.id = self.next_id
        self.next_id += 1
        self.tasks[task.id] = copy.copy(task)
        return task

    def get(self, task_id):
        if task_id not in self.tasks:
            raise NotFound(f"task {task_id} not found")
        return copy.copy(self.tasks[task_id])

    def save(self, task):
        self.tasks[task.id] = copy.copy(task)
    ...
```

The chapter shows the lie in numbers: a lazy fake answers `'new title'` for a service that forgot `save`, while the careful fake and real SQLite both answer `'old title'`. Only the **contract tests** (the same tests run against both implementations) keep the fake honest: if the fake drifts from the database, a test fails in one parameter and not in the other.

## Complexity

`open_count_for` and `list_for_project` scan the dictionary, which is fine for a fake (a test double is not a database).

## Another way

For SQLite the in-memory database is already a very good test double (chapter 6.2 measured it at about the same speed as the fake). The fake earns its keep when the real database is slow to start (PostgreSQL, a remote service) or when you want to inject failures that are hard to trigger in SQL.
