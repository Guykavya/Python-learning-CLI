# A fake that keeps the contract

Chapter sections 6.1 (a fake repository), 6.2 (unit tests of the rules without a database) and 6.3 (fakes can lie: contract tests). A **fake** is a small working in-memory version of a repository. Services that only use the repository's methods can be handed the fake, and every rule is then tested with no SQL, no file and no web server.

A fake is code, and code has bugs. If it behaves differently from the real repository, your fast tests pass while production fails. The cure is a **contract test**: one set of tests for the repository interface that runs against **every** implementation. If the fake and the SQL version pass the same tests, they agree.

## What to write

`Task` and `NotFound` are given. Write `FakeTaskRepo()` with **exactly the interface of the SQLite repository of problem p005**:

```python
class FakeTaskRepo:
    def __init__(self): ...
    def add(self, task) -> Task: ...                              # sets task.id (1, 2, 3, ...); returns the same task
    def get(self, task_id) -> Task: ...                           # a NEW Task each time; raises NotFound
    def save(self, task) -> None: ...
    def open_count_for(self, user_id) -> int: ...                 # tasks of that user whose status is not 'done'
    def list_for_project(self, project_id, status=None) -> list[Task]: ...   # ordered by id, optional status filter
```

The classic way a fake lies (chapter 6.3): a real database hands out a **new object on every `get`**, so a service that changes the object and forgets to call `save` loses the change. A lazy fake that stores and returns the *same* object hides that bug. Your fake must therefore **copy in and out**: store a copy in `add` and `save`, and return a copy from `get` and `list_for_project`. (`copy.copy` is enough for this flat dataclass.)

The tests run **the same contract tests** against your fake and against the real SQLite repository (given to the tests), and both must pass.

## Example

```python
repo = FakeTaskRepo()
t = repo.add(Task(None, 1, "old", "todo", None, "now"))
again = repo.get(t.id)
again.title = "changed but not saved"
repo.get(t.id).title        # 'old'   <- just like the real database
```
