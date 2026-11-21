## Approach

```python
class SqliteUnitOfWork:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = connect(self.path)
        repos = SqliteRepos(self.conn)
        self.tasks, self.projects, self.users = repos.tasks, repos.projects, repos.users
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.rollback()
        self.conn.close()

    def commit(self):
        self.conn.commit()
```

Notice that `__exit__` **always** calls `rollback()`: after a `commit()` it does nothing, after a failure it undoes the work, and a forgotten `commit()` cannot leave half a change behind (worst case nothing is saved, and a test notices). What it fixes (chapter 7.4): a failed request leaves no traces; requests no longer interfere through one shared connection (each use case has its own); and the transaction stopped being a convention ("remember to call `run`") and became an object you cannot forget.

## Cost

One class of 14 lines, one fake with a deep copy for tests (p013), and the rule "a service must open `with uow:` and call `commit()` itself". For SQLite a connection per request is cheap; with PostgreSQL you would borrow one from a pool.

## Another way

SQLAlchemy's `Session` already is a unit of work (it tracks changes and commits them together) and Django has `transaction.atomic()`. You do not need to reinvent this in a real project, but you must understand the pattern to use those tools well: we built it by hand once so nothing is magic.
