# Refactor where it hurts, and write it down

Chapter section 19 (the project: refactor the task API where it actually hurts, and document why) and the whole chapter before it. This is the second outcome of the module in practice: you refactor **only** where there is a concrete pain, you **prove** it with tests, and you **write down** why. The starter is the Taskboard of chapter 2.2: everything in the routes, with one shared SQLite connection. It passes the 8 tests that describe its behaviour from the outside (the **safety net**), and it fails the 3 tests that expose its pains (chapter 3):

1. rule 3 (at most 3 open tasks) is enforced when a task is **created**, but not when it is **assigned by `PATCH`** or **reopened**;
2. a failed request (the mail provider rejects the address) leaves a **half-saved task** that the next, unrelated request commits;
3. rules, SQL, e-mail and JSON are one block, so checking one rule needs HTTP and a database.

## What to deliver (in `solution.py`)

`SCHEMA`, `MAX_OPEN`, `ALLOWED`, the domain errors (`DomainError`, `NotFound`, `InvalidInput`, `RuleViolation`) and the `Task` dataclass are given. Build the three layers of chapters 4 to 7, **one remedy at a time**, until all the tests pass, **without changing the HTTP behaviour** (the 8 safety-net tests stay as they are):

**1. A service layer.** Four use cases, each taking a **unit of work** and the **mailer** (an object with `send_email(to, subject)`), raising **domain errors** only (no HTTP in them):

```python
def create_task(uow, mailer, project_id, title, assignee_id=None) -> Task: ...
def update_task(uow, mailer, task_id, assignee_id=None, status=None) -> Task: ...
def get_task(uow, task_id) -> Task: ...
def list_tasks(uow, project_id, status=None) -> list[Task]: ...
```

Each starts with `with uow:` and calls `uow.commit()` **once**, at the end, when it writes. The rules are those of chapter 2.1 (title 1 to 120 characters after trimming, membership, rule 3 on **all three** paths, the status flow, `completed_at`, one audit line per change, one e-mail per assignment: `"New task: <title>"` at creation, `"Task assigned: <title>"` on `PATCH`). Check the rules **before** the e-mail and the writes.

**2. A repository.** All SQL in repository classes with this interface (the services may only use these methods):

```text
uow.tasks:     add(task) -> task with its id        get(task_id) -> Task, raises NotFound      save(task)
               list_for_project(project_id, status=None) -> [Task] ordered by id      open_count_for(user_id) -> int (not done)
               add_audit(task_id, action, at)       audit_for(task_id) -> [action, ...]
uow.projects:  exists(project_id)                   is_member(project_id, user_id)
uow.users:     email_of(user_id)
```

**3. A unit of work.** `SqliteUnitOfWork(path)`: a context manager that opens **its own connection** in `__enter__` (with the Taskboard schema), exposes `tasks`, `projects`, `users` bound to that connection, `commit()`, and in `__exit__` **always** rolls back and closes. Each request uses a **new** one.

**4. `create_app(db_path, mailer)`**: the composition root. The routes only translate: parse the request, call **one** service function with a new `SqliteUnitOfWork(db_path)`, turn the returned `Task` into JSON (`id`, `project_id`, `title`, `status`, `assignee_id`, `completed_at`), and **one** exception handler turns `DomainError` into HTTP (`NotFound` 404, `InvalidInput` 422, `RuleViolation` 409). The routes no longer raise `HTTPException`.

**5. Write it down.**

- `ADR`: a string with an architecture decision record in Markdown: a title line (`# ADR 0001: ...`) and the sections `## Status`, `## Context`, `## Decision`, `## Consequences`, `## Alternatives`, each with real content (what hurt, with evidence; what you decided; what it costs; what you did **not** do and why).
- `PAIN_LOG`: a list of rows, one per layer you added: `{"pain": ..., "evidence": ..., "remedy": "service layer" | "repository" | "unit of work"}`. Evidence is something you can re-check (a failing test, a count, a timing), not "it is messy".

## How it is tested

The **safety net** (8 HTTP tests of the chapter, unchanged) and the **3 pain tests** run through HTTP against your `create_app`. Then the layers themselves: the rules run through **a fake unit of work** (given to the tests; it implements the repository interface above, in memory, with real transaction semantics: the use case works on a private copy that replaces the store only on `commit()`), in well under half a second; a real `SqliteUnitOfWork` on a file commits and rolls back; **no SQL** may remain outside the repository classes and `connect()`, and no service function may mention SQL or HTTP; and the ADR and the pain log are checked for **structure** only (the sections are there and say something; every layer has a pain with evidence). Whether your decisions are wise is for a reviewer, or for you in three months, to judge by reading them.

## Example

```python
uow = SqliteUnitOfWork("taskboard.db")
create_task(uow, mailer, 1, "Write docs", assignee_id=1)     # a Task; the e-mail was sent; the task, its audit line committed together
update_task(SqliteUnitOfWork("taskboard.db"), mailer, 1, assignee_id=2)    # RuleViolation if Ben already has 3 open tasks: on EVERY path
```

Chapter 19.1 asks you to refactor only where it hurts, and to say what you did **not** add. This version of the project covers the first three rungs of the ladder (service layer, repository, unit of work). The domain model and the outbox (chapters 8 and 9) are the next rungs: p011 to p014 let you practise them; add them to this project only if your pain log shows the pain (the ADR's "Alternatives" is the place to say so).
