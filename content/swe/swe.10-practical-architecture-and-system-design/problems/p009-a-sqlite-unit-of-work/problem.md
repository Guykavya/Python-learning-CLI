# A SQLite unit of work

Chapter section 7 (layer 3: the unit of work). Two things are still wrong with a **shared global connection**: the transaction is a convention ("call `run`"), and requests interfere. In the chapter, request A inserts, request B fails and rolls back the **shared** connection, and A's work is gone. The cure is: **every use case gets its own connection, and one object owns its transaction from start to finish.** That object is the **unit of work**.

A unit of work (UoW) does four things:

1. **opens** a connection at the start of the use case (`with uow:`);
2. **provides** the repositories, all bound to that **same connection**, so they share one transaction;
3. **commits** when the service says so (`uow.commit()`);
4. **rolls back and closes** when the block ends, always: after a commit the rollback does nothing, after a failure or a forgotten commit it undoes the work.

## What to write

`connect(path)` and the repositories (`SqliteTaskRepo`, `SqliteProjectRepo`, `SqliteUserRepo`, bundled in `SqliteRepos`) are **given** in the starter. Write only the unit of work:

```python
class SqliteUnitOfWork:
    def __init__(self, path): ...
    def __enter__(self): ...                  # open a connection, build the repositories, return self
    def __exit__(self, exc_type, exc, tb): ...# rollback, close; never swallow an exception
    def commit(self): ...
```

After `__enter__` the object has the attributes `conn`, `tasks`, `projects` and `users`. The attributes `tasks`, `projects`, `users` are the repositories of `SqliteRepos(self.conn)`, so they all use `self.conn`. A fresh connection is opened on **every** `__enter__` (the same `SqliteUnitOfWork` object can be used for several `with` blocks, one after the other).

## Example

```python
uow = SqliteUnitOfWork(path)
with uow:
    uow.tasks.add(Task(None, 1, "x", "todo", None, "now"))
    uow.commit()                      # saved
with uow:
    uow.tasks.add(Task(None, 1, "y", "todo", None, "now"))
    # no commit: leaving the block undoes it
with SqliteUnitOfWork(path) as check:
    [t.title for t in check.tasks.list_for_project(1)]      # ['x']
```

Four lines of logic. Notice that `__exit__` **always** calls `rollback()`: a forgotten `commit()` can never leave half a change behind; the worst that happens is that nothing is saved, which a test notices at once.
