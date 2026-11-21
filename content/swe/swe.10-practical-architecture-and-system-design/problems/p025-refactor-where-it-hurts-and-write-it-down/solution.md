## Approach

The full code is `reference.py`. The order of work (the chapter's, with the test run after each step):

1. **Service layer** (chapter 4): `create_task` and `update_task` hold the rules, raise `NotFound` / `InvalidInput` / `RuleViolation`, and call `_check_capacity` from all three paths (create, assign, reopen), with the two hidden decisions (a done task and the same person need no free slot). The two forgotten-rule tests turn green.
2. **Repository** (chapters 5 and 6): `SqliteTaskRepo`, `SqliteProjectRepo`, `SqliteUserRepo`, in business words (`open_count_for`, `list_for_project`); the services contain no SQL; the fake unit of work of the tests can stand in for the real one.
3. **Unit of work** (chapter 7): `SqliteUnitOfWork` with its own connection and an `__exit__` that always rolls back. The third pain test turns green: a failed request can no longer be committed by the next one.
4. **Composition root**: `create_app(db_path, mailer)` with one `DomainError` handler and thin routes.
5. **Documents**: the ADR and the pain log are the **why**, written while the evidence is fresh.

```python
class SqliteUnitOfWork:
    def __enter__(self):
        self.conn = connect(self.path)
        self.tasks, self.projects, self.users = SqliteTaskRepo(self.conn), SqliteProjectRepo(self.conn), SqliteUserRepo(self.conn)
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.rollback()
        self.conn.close()
```

**The bill** (chapter 10.3): the program roughly doubles in size (the starter is about 130 lines in one function; the finished solution about 330 lines in layers) and the number of tests goes from 8 to over 30, most of them pure Python that runs in milliseconds. It bought three concrete things, each tied to a pain you measured: one place for rule 3, no half-saved data, rules that run without HTTP and a database. If your own project does not have those pains, you should **not** pay this price (chapter 10.4).

## Cost

About 200 more lines of program and the discipline of the interface. Nothing here needs a framework: services are functions, repositories are small classes, the unit of work is a context manager.

## Another way

Stop earlier: for a small app the service layer plus `run()` helper (chapter 4.3) already fixes two of the three pains. Go further only when the pain log says so: a **domain model** when rules about one object's state are scattered (p011), an **outbox** when a side effect must not be lost or sent for a rolled-back change (p013), **separate services** when people or load demand it (p016).
