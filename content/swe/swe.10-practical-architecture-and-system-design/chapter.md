# Chapter 10 (SWE): Practical architecture and system design

Most "architecture" advice sounds like a list of boxes you must draw: controllers, services, repositories, events, queues, microservices. Beginners copy the boxes. They get code that is longer, harder to follow, and no better. Experienced engineers do the opposite: they **start with the simplest thing that works, notice where it hurts, and add exactly one layer that removes that pain**. Architecture is a set of answers to the question "what will be hard to change later, and what can I do about it now?"

This chapter teaches that habit with a real, running example. You will take a small task-management API, the kind you built in swe.05, and refactor it **step by step**. After each step you will see the test that proves the behaviour did not change, and the specific pain that the new layer removed. Then we zoom out: monolith or microservices, how to talk to other services safely, and how to think about **system design** (traffic estimates, load balancing, replicas, sharding, CAP) so that you can sketch a design for a common app and defend your trade-offs.

By the end you reach two outcomes:

- You can **explain what concrete pain a repository layer removes in your own project**, and when it would only add noise (sections 3 to 10).
- You can **sketch a system design for a common app and discuss its trade-offs**: requirements, numbers, a diagram, the bottleneck and the failure modes (sections 13 to 18).

Prerequisites: swe.03 (SQL, transactions), swe.05 (FastAPI and the task-management project), swe.08 (queues, idempotency, the outbox idea), core.22 (Pythonic design and patterns: composition, protocols). If a word like "transaction" or "idempotent" is hazy, re-read the relevant chapter first.

> **Offline rule for this chapter.** Everything runs on SQLite, the standard library, FastAPI's `TestClient` and pytest. No Postgres, no Docker, no cloud. Real systems appear as drawings, numbers and code you can read. Every output in this chapter was produced by running the code above it, with these versions (patch versions and timings may differ on your machine):

```bash run
python -c "
import sys, sqlite3, fastapi, pydantic, pytest
print('python  ', sys.version.split()[0])
print('sqlite  ', sqlite3.sqlite_version)
print('fastapi ', fastapi.__version__)
print('pydantic', pydantic.__version__)
print('pytest  ', pytest.__version__)
"
```
```text
python   3.14.4
sqlite   3.46.1
fastapi  0.162.0
pydantic 2.14.3
pytest   9.1.1
```

## Table of contents

1. [Architecture is about change](#1-architecture-is-about-change)
2. [The example we will refactor: Taskboard](#2-the-example-we-will-refactor-taskboard)
3. [Finding the pain](#3-finding-the-pain)
4. [Layer 1: the service layer](#4-layer-1-the-service-layer)
5. [Layer 2: the repository](#5-layer-2-the-repository)
6. [Fakes, contract tests, and what a repository really buys you](#6-fakes-contract-tests-and-what-a-repository-really-buys-you)
7. [Layer 3: the unit of work](#7-layer-3-the-unit-of-work)
8. [The domain model: rules live with the data they protect](#8-the-domain-model-rules-live-with-the-data-they-protect)
9. [Events and the outbox](#9-events-and-the-outbox)
10. [The finished shape, and when not to build it](#10-the-finished-shape-and-when-not-to-build-it)
11. [Monolith, modular monolith or microservices?](#11-monolith-modular-monolith-or-microservices)
12. [Talking to other services safely](#12-talking-to-other-services-safely)
13. [System design: a method, not a bag of tricks](#13-system-design-a-method-not-a-bag-of-tricks)
14. [Scaling out the application tier](#14-scaling-out-the-application-tier)
15. [Scaling the data tier: replicas, partitions and CAP](#15-scaling-the-data-tier-replicas-partitions-and-cap)
16. [Worked design 1: a URL shortener](#16-worked-design-1-a-url-shortener)
17. [Worked design 2: activity feed and notifications for Taskboard](#17-worked-design-2-activity-feed-and-notifications-for-taskboard)
18. [Writing it down: design documents and decision records](#18-writing-it-down-design-documents-and-decision-records)
19. [Project: refactor the task API where it actually hurts, and document why](#19-project-refactor-the-task-api-where-it-actually-hurts-and-document-why)
20. [Common traps](#20-common-traps)
21. [Collected traps](#21-collected-traps)
22. [Summary](#22-summary)

## 1. Architecture is about change

### 1.1 What "architecture" means in practice

**Architecture** is the set of decisions that are **expensive to change later**. Naming a local variable is not architecture, because you can change it in a second. Choosing where the business rules live, who owns a transaction, whether two parts of the system talk through function calls or through HTTP, or whether the database is shared: those are architecture, because changing them later means touching many files, many teams, or live data.

Good architecture does not predict the future. It keeps the **cost of change low in the places where change is likely**. A web shop will change its discount rules every month; it will almost never change from "orders have lines" to something else. So the discount rules deserve a clean home, and the order-line table does not.

### 1.2 Two ways to fail

| Failure | What it looks like | Why it happens |
|---|---|---|
| **Big ball of mud** | One 900-line `views.py`. Every route has SQL, rules, e-mail sending and JSON building mixed together. Fixing one rule means finding it in five places. | No structure was ever added; "it works" was the only goal. |
| **Architecture astronaut** | A todo app with 14 packages, an interface for every class, a message bus, and three microservices. A new field means editing nine files. | Boxes were copied from a book *before* any pain existed. |

Both are expensive. The mud makes change slow and risky. The astronaut makes **every** change slow, including the easy ones, and hides the real logic behind indirection. The goal of this chapter is the narrow path between them.

### 1.3 The rule: pain first, layer second

Before you add any layer, answer three questions **in writing**:

1. **What concrete pain do I have?** Not "it might get messy" but "the rule 'a user may have at most 3 open tasks' is checked in two routes and forgotten in a third", or "to test one rule I must start a web server and a database".
2. **How will I know it is fixed?** A test that failed and now passes, a number that went down, a file that got shorter.
3. **What does the layer cost?** Every layer adds files, names to learn, and one more place a reader must jump to. Be honest about that cost.

If you cannot answer question 1 with something you have actually seen, **do not add the layer yet**. Writing the code without the layer is not a failure; it is how you find out what the right layer is.

### 1.4 A ladder from pain to remedy

Here is the map for this chapter. Each row is a pain you will meet in real projects, and the smallest remedy for it. You read the table from the top, and stop as soon as the pain is gone.

| Pain you can point at | Smallest remedy | Section |
|---|---|---|
| The same rule is copied into several routes and drifts apart | A **service layer**: one function per use case, routes become thin | 4 |
| Business code is full of SQL; tests need a real database; switching storage touches everything | A **repository**: one object that hides how data is stored | 5, 6 |
| Several writes must succeed or fail together; a failed request leaves half a change behind | A **unit of work**: one object that owns the transaction | 7 |
| Rules are scattered over `if` statements next to data they protect | A **domain model**: objects that guard their own rules | 8 |
| Something must happen *because* something else happened (send e-mail after a task is assigned), and it must not be lost or sent twice | **Domain events** and an **outbox** | 9 |
| One team cannot deploy without waiting for another; one part needs 50 servers and the rest needs 1 | Separate **deployable services** (last, not first) | 11, 12 |

Notice what is *not* in the first column: "my code does not look like the book". Style is not pain.

### 1.5 Costs of a layer

Every layer you add has a bill. Here is a realistic one for adding a repository layer to a small CRUD route:

| Cost | Example |
|---|---|
| More files and names | `repo.py`, `FakeRepo`, `TaskRow`, a mapper function |
| One more jump when reading | "where does `get_task` actually run SQL?" needs two clicks, not zero |
| Mapping code | rows in, objects out, objects in, rows out |
| Risk of fakes that lie | the in-memory fake behaves differently from the real database |

A layer is worth it when the pain it removes is bigger than this bill. For a script with one table and no rules, the bill is bigger. For an API with money, permissions and several writers, the pain is bigger. This is a **judgement**, and you will make it better with practice. The rest of the chapter gives you evidence to judge with.

### Try it: pain or style?

For each statement, decide if it describes a concrete *pain* (worth a layer) or a *style preference* (not yet): (a) "My routes do not follow clean architecture." (b) "Three routes check that the user is a project member, and last week I fixed a bug in two of them." (c) "I want to switch from SQLite to Postgres next year, so I will write interfaces for everything now." (d) "Testing the 'max 3 open tasks' rule takes a database, a web client and 40 lines of setup."

<details><summary>Answer</summary>

(a) **Style.** No bug, no cost, no measurement. (b) **Pain.** Duplicated rule, already caused a bug: a service layer (or a shared function) pays off now. (c) **Speculation.** Switching databases is possible but rarely happens; and when it does, the SQL dialects differ anyway, so empty interfaces written today would not save you. Wait for the pain, or for a decision date. (d) **Pain.** Slow, heavy tests discourage testing: this is the classic reason for a repository and a fake.

</details>

## 2. The example we will refactor: Taskboard

### 2.1 What it does

**Taskboard** is a small version of the task-management API from swe.05. It has users, projects, project members and tasks. The API:

| Route | What it does |
|---|---|
| `POST /projects/{id}/tasks` | create a task, optionally assigned to a member |
| `PATCH /tasks/{id}` | assign the task and/or change its status |
| `GET /tasks/{id}` | read one task |
| `GET /projects/{id}/tasks?status=` | list tasks of a project |

And these business rules, which are the heart of the program:

1. A title has 1 to 120 characters after trimming spaces.
2. A task can only be assigned to a **member of its project**.
3. A user may have **at most 3 open tasks** (any status except `done`) at once. We call this the *work-in-progress limit*, or WIP limit.
4. Status moves along `todo → doing → done`. Allowed moves are: `todo→doing`, `doing→todo`, `doing→done`, and reopening `done→todo`. Everything else (for example `todo→done`) is rejected.
5. Moving to `done` records `completed_at`; reopening clears it. A reopened task counts as open again, so rule 3 applies to it too.
6. Every change writes a line to an `audit` table, and assigning a task e-mails the assignee.

Rules 3 and 5 together are what make this example interesting: the same rule must be enforced from **three different entry points** (create, assign, reopen).

### 2.2 The first version: everything in the route

We start the way most real projects start. We write the code straight, with SQL in the route handlers. This is **not a bad first version**. It is short, it is easy to follow, and it works. First the schema and a deliberately simple database module:

```python
# taskboard/__init__.py
```

```python
# taskboard/schema.py
SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY, name TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS members (
    project_id INTEGER NOT NULL REFERENCES projects(id),
    user_id    INTEGER NOT NULL REFERENCES users(id),
    PRIMARY KEY (project_id, user_id));
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    project_id INTEGER NOT NULL REFERENCES projects(id),
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'todo',
    assignee_id INTEGER REFERENCES users(id),
    created_at TEXT NOT NULL,
    completed_at TEXT);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY, task_id INTEGER, action TEXT NOT NULL, at TEXT NOT NULL);
"""
```

```python
# taskboard/db.py
import os
import sqlite3

from .schema import SCHEMA

_conn = None


def get_conn():
    """One shared connection for the whole process (simple, and a trap: see section 3)."""
    global _conn
    if _conn is None:
        _conn = sqlite3.connect(os.environ.get("TASKBOARD_DB", "taskboard.db"),
                                check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.execute("PRAGMA foreign_keys = ON")
        _conn.executescript(SCHEMA)
    return _conn


def reset():
    """Close and forget the shared connection (tests use this)."""
    global _conn
    if _conn is not None:
        _conn.close()
    _conn = None
```

A tiny fake e-mail module. It records what was "sent" and refuses addresses starting with `bounce`, so we can test failure:

```python
# taskboard/mailer.py
SENT = []          # (to, subject) pairs; a real mailer would talk to SMTP or a provider


class MailError(Exception):
    pass


def send_email(to, subject):
    if to.startswith("bounce"):
        raise MailError(f"provider rejected {to}")
    SENT.append((to, subject))
```

And the application, in one file:

```python
# taskboard/main.py
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import db, mailer

app = FastAPI(title="Taskboard")
MAX_OPEN = 3


class NewTask(BaseModel):
    title: str
    assignee_id: int | None = None


class TaskPatch(BaseModel):
    assignee_id: int | None = None
    status: str | None = None


def now():
    return datetime.now(timezone.utc).isoformat()


@app.post("/projects/{project_id}/tasks", status_code=201)
def create_task(project_id: int, body: NewTask):
    conn = db.get_conn()
    title = body.title.strip()
    if not title or len(title) > 120:
        raise HTTPException(422, "title must have 1 to 120 characters")
    if conn.execute("SELECT 1 FROM projects WHERE id = ?", (project_id,)).fetchone() is None:
        raise HTTPException(404, "project not found")
    if body.assignee_id is not None:
        member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                              (project_id, body.assignee_id)).fetchone()
        if member is None:
            raise HTTPException(409, "assignee is not a member of this project")
        open_count = conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'",
            (body.assignee_id,)).fetchone()[0]
        if open_count >= MAX_OPEN:
            raise HTTPException(409, f"assignee already has {MAX_OPEN} open tasks")
    stamp = now()
    cur = conn.execute(
        "INSERT INTO tasks (project_id, title, status, assignee_id, created_at) "
        "VALUES (?, ?, 'todo', ?, ?)", (project_id, title, body.assignee_id, stamp))
    task_id = cur.lastrowid
    conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'created', ?)",
                 (task_id, stamp))
    if body.assignee_id is not None:
        email = conn.execute("SELECT email FROM users WHERE id = ?",
                             (body.assignee_id,)).fetchone()[0]
        mailer.send_email(email, f"New task: {title}")
    conn.commit()
    return {"id": task_id, "title": title, "status": "todo", "assignee_id": body.assignee_id}


ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, body: TaskPatch):
    conn = db.get_conn()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        raise HTTPException(404, "task not found")
    stamp = now()
    if body.assignee_id is not None:
        member = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                              (task["project_id"], body.assignee_id)).fetchone()
        if member is None:
            raise HTTPException(409, "assignee is not a member of this project")
        conn.execute("UPDATE tasks SET assignee_id = ? WHERE id = ?", (body.assignee_id, task_id))
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'assigned', ?)",
                     (task_id, stamp))
        email = conn.execute("SELECT email FROM users WHERE id = ?",
                             (body.assignee_id,)).fetchone()[0]
        mailer.send_email(email, f"Task assigned: {task['title']}")
    if body.status is not None:
        if (task["status"], body.status) not in ALLOWED:
            raise HTTPException(409, f"cannot move from {task['status']} to {body.status}")
        completed = stamp if body.status == "done" else None
        conn.execute("UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                     (body.status, completed, task_id))
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, ?, ?)",
                     (task_id, f"status:{body.status}", stamp))
    conn.commit()
    return _task_json(conn, task_id)


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = db.get_conn()
    if conn.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone() is None:
        raise HTTPException(404, "task not found")
    return _task_json(conn, task_id)


@app.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int, status: str | None = None):
    conn = db.get_conn()
    sql = "SELECT id FROM tasks WHERE project_id = ?"
    args = [project_id]
    if status is not None:
        sql += " AND status = ?"
        args.append(status)
    ids = [r["id"] for r in conn.execute(sql + " ORDER BY id", args)]
    return [_task_json(conn, i) for i in ids]


def _task_json(conn, task_id):
    t = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return {"id": t["id"], "project_id": t["project_id"], "title": t["title"],
            "status": t["status"], "assignee_id": t["assignee_id"],
            "completed_at": t["completed_at"]}
```

That is about 120 lines and it does everything. Read it once, slowly. You should be able to point to the rules from section 2.1 inside it. We will return to it, so keep it in mind.

### 2.3 The safety net: tests that talk HTTP

Before touching working code you need **tests that describe its behaviour from the outside**. These API tests only use HTTP and the database file. They do not import any internal function, so they will keep passing through every refactor in this chapter. If they ever fail after a change, you broke behaviour. That is the definition of a safe refactoring: *the outside does not change*.

First the test data: a few users and projects that every test starts from (users 1, 2 and 4 are members of project 1; user 3 belongs to project 2 only; user 4's e-mail address is rejected by our fake mail provider):

```python
# tests/seed.py
SEED = """
INSERT INTO users (id, name, email) VALUES
  (1, 'Ana',    'ana@example.com'),
  (2, 'Ben',    'ben@example.com'),
  (3, 'Cy',     'cy@example.com'),
  (4, 'Bounce', 'bounce@example.com');
INSERT INTO projects (id, name) VALUES (1, 'Website'), (2, 'Other');
INSERT INTO members (project_id, user_id) VALUES (1, 1), (1, 2), (1, 4), (2, 3);
"""
```

Then a fixture that builds a fresh database with that data for every test:

```python
# tests/conftest.py
import sqlite3

import pytest
from fastapi.testclient import TestClient

from taskboard import db, mailer, main
from seed import SEED
from taskboard.schema import SCHEMA


@pytest.fixture
def client(tmp_path, monkeypatch):
    path = tmp_path / "taskboard.db"
    monkeypatch.setenv("TASKBOARD_DB", str(path))
    db.reset()
    mailer.SENT.clear()
    seed = sqlite3.connect(path)
    seed.executescript(SCHEMA + SEED)
    seed.close()
    yield TestClient(main.app, raise_server_exceptions=False)
    db.reset()
```

Now the tests, one per rule:

```python
# tests/test_api.py
def make(client, title="Write docs", assignee=None, project=1):
    return client.post(f"/projects/{project}/tasks", json={"title": title, "assignee_id": assignee})


def test_create_unassigned_task(client):
    r = make(client)
    assert r.status_code == 201, r.text
    assert r.json()["status"] == "todo"


def test_title_is_trimmed_and_validated(client):
    assert make(client, title="   x  ").json()["title"] == "x"
    assert make(client, title="   ").status_code == 422, "blank titles must be rejected"
    assert make(client, title="a" * 121).status_code == 422, "121 characters is too long"


def test_unknown_project_is_404(client):
    assert make(client, project=99).status_code == 404


def test_only_members_can_be_assigned(client):
    assert make(client, assignee=3).status_code == 409, "user 3 is not in project 1"
    assert make(client, assignee=1).status_code == 201


def test_assigning_sends_one_email(client):
    from taskboard import mailer
    make(client, title="Ship it", assignee=1)
    assert mailer.SENT == [("ana@example.com", "New task: Ship it")]


def test_wip_limit_on_create(client):
    for i in range(3):
        assert make(client, title=f"t{i}", assignee=1).status_code == 201
    assert make(client, title="t3", assignee=1).status_code == 409, "a 4th open task must be refused"
    assert make(client, title="t3", assignee=2).status_code == 201, "other users are unaffected"


def test_status_flow(client):
    tid = make(client).json()["id"]
    move = lambda s: client.patch(f"/tasks/{tid}", json={"status": s})
    assert move("done").status_code == 409, "todo -> done is not allowed"
    assert move("doing").status_code == 200
    r = move("done")
    assert r.status_code == 200 and r.json()["completed_at"] is not None
    assert move("doing").status_code == 409, "done -> doing is not allowed"
    r = move("todo")
    assert r.status_code == 200 and r.json()["completed_at"] is None, "reopening clears completed_at"


def test_list_filters_by_status(client):
    a = make(client, title="a").json()["id"]
    make(client, title="b")
    client.patch(f"/tasks/{a}", json={"status": "doing"})
    assert [t["title"] for t in client.get("/projects/1/tasks").json()] == ["a", "b"]
    assert [t["title"] for t in client.get("/projects/1/tasks?status=doing").json()] == ["a"]
```

```bash run
python -m pytest -q -p no:cacheprovider tests/test_api.py
```
```text
........                                                                 [100%]
8 passed in 0.18s
```

Eight tests pass. These are the **characterisation tests** of our program: they describe what it does today. Notice they cover each rule at least once, except one, which we will discover in the next section.

## 3. Finding the pain

Now do what the rule in section 1.3 says: look for **concrete pain** before changing anything. Keep a short **pain log**: what happened, how you know, what it costs. We will make four discoveries, each with evidence.

### 3.1 Pain 1: a rule copied into several places, and forgotten in one

Search for the WIP limit (rule 3). Where does the program enforce it?

```bash run
grep -n "MAX_OPEN\|open_count" taskboard/main.py
```
```text
9:MAX_OPEN = 3
39:        open_count = conn.execute(
42:        if open_count >= MAX_OPEN:
43:            raise HTTPException(409, f"assignee already has {MAX_OPEN} open tasks")
```

It appears **once**, in `create_task`. But rule 3 says a user has at most 3 open tasks, whatever way they got the task. Assigning an existing task to someone (`PATCH`) and reopening a done task are two more ways. Let us write the tests that a careful teammate would write after reading the rules:

```python
# tests/test_pain.py
def make(client, title="Write docs", assignee=None, project=1):
    return client.post(f"/projects/{project}/tasks", json={"title": title, "assignee_id": assignee})


def fill_ana(client):
    """Give Ana (user 1) three open tasks."""
    for i in range(3):
        assert make(client, title=f"busy{i}", assignee=1).status_code == 201


def test_assign_by_patch_respects_wip_limit(client):
    fill_ana(client)
    loose = make(client, title="loose").json()["id"]
    r = client.patch(f"/tasks/{loose}", json={"assignee_id": 1})
    assert r.status_code == 409, "assigning a 4th open task through PATCH must be refused too"


def test_reopen_respects_wip_limit(client):
    first = make(client, title="old", assignee=1).json()["id"]
    client.patch(f"/tasks/{first}", json={"status": "doing"})
    client.patch(f"/tasks/{first}", json={"status": "done"})
    fill_ana(client)                                   # Ana now has 3 other open tasks
    r = client.patch(f"/tasks/{first}", json={"status": "todo"})
    assert r.status_code == 409, "reopening makes the task open again: that would be a 4th"


def test_failed_email_leaves_no_half_saved_task(client):
    r = make(client, title="for bounce", assignee=4)   # the mail provider rejects this address
    assert r.status_code == 500
    make(client, title="next")                         # an unrelated, perfectly valid request
    titles = [t["title"] for t in client.get("/projects/1/tasks").json()]
    assert titles == ["next"], f"the failed request left traces behind: {titles}"
```

```bash run
python -m pytest -q -p no:cacheprovider --tb=line tests/test_pain.py
```
```text
FFF                                                                      [100%]
=================================== FAILURES ===================================
E   AssertionError: assigning a 4th open task through PATCH must be refused too
    assert 200 == 409
     +  where 200 = <Response [200 OK]>.status_code
/home/you/taskboard_project/tests/test_pain.py:15: AssertionError: assigning a 4th open task through PATCH must be refused too
E   AssertionError: reopening makes the task open again: that would be a 4th
    assert 200 == 409
     +  where 200 = <Response [200 OK]>.status_code
/home/you/taskboard_project/tests/test_pain.py:24: AssertionError: reopening makes the task open again: that would be a 4th
E   AssertionError: the failed request left traces behind: ['for bounce', 'next']
    assert ['for bounce', 'next'] == ['next']
      
      At index 0 diff: 'for bounce' != 'next'
      Left contains one more item: 'next'
      Use -v to get more diff
/home/you/taskboard_project/tests/test_pain.py:32: AssertionError: the failed request left traces behind: ['for bounce', 'next']
=========================== short test summary info ============================
FAILED tests/test_pain.py::test_assign_by_patch_respects_wip_limit - Assertio...
FAILED tests/test_pain.py::test_reopen_respects_wip_limit - AssertionError: r...
FAILED tests/test_pain.py::test_failed_email_leaves_no_half_saved_task - Asse...
3 failed in 0.15s
```

All three fail. These are **bugs that the original eight tests could not see**. Look at what they say:

- **PATCH assign** and **reopen** silently skip rule 3. The rule was written in one route and forgotten in two others. Nobody did anything silly: each handler is a separate block of code, and copying a rule into each one is easy to forget. This is the first, most common pain.
- **The third failure is different and worse.** The task `for bounce` was inserted, then the e-mail raised an error, then the handler crashed *before* `commit()`. But `db.get_conn()` gives every request the **same shared connection**, so the half-finished insert stayed inside the open transaction. The next, unrelated request (`next`) called `commit()` and **committed the orphan task too**. A failed request changed the data of a later successful one.

### 3.2 Pain 2: a test for one rule needs the whole stack

Look at `test_wip_limit_on_create` in the safety net. To check a single rule, "the 4th task is refused", it needs: a web client, JSON, a temporary database file, a seeded schema, and four HTTP calls. It is fast enough here, but every new rule test pays the same set-up price, and the failure message is "409 != 201" with no hint where the problem is.

Measure the cost of one rule check through HTTP with a small script (the numbers depend on your machine; the ratio is what matters):

```python
# measure_http.py
import sqlite3, tempfile, os, time
from fastapi.testclient import TestClient
from taskboard import db, main
from taskboard.schema import SCHEMA

tmp = tempfile.mkdtemp()
os.environ["TASKBOARD_DB"] = os.path.join(tmp, "m.db")
db.reset()
c = sqlite3.connect(os.environ["TASKBOARD_DB"])
c.executescript(SCHEMA + "INSERT INTO users VALUES (1,'Ana','ana@example.com'); INSERT INTO projects VALUES (1,'P'); INSERT INTO members VALUES (1,1);")
c.close()
client = TestClient(main.app)
n = 200
start = time.perf_counter()
for i in range(n):
    client.post("/projects/1/tasks", json={"title": f"t{i}"})
elapsed = time.perf_counter() - start
print(f"{n} creates through HTTP + SQLite: {elapsed / n * 1000:.2f} ms each")
```

```bash run
python measure_http.py
```
```text
200 creates through HTTP + SQLite: 3.77 ms each
```

A plain function call that checks `open_count >= 3` takes well under a microsecond. The HTTP test is thousands of times slower, and, more importantly, it can only be written *after* the whole web layer and database are running. In section 6 we will compare with a unit test of the same rule.

### 3.3 Pain 3: business rules and SQL are one block of code

Count how many different kinds of work one route does:

```bash run
python - <<'EOF'
import re
src = open("taskboard/main.py").read()
print("SQL statements in main.py:", len(re.findall(r"conn\.execute\(", src)))
print("HTTPException raises     :", src.count("raise HTTPException"))
print("lines in main.py         :", src.count("\n") + 1)
EOF
```
```text
SQL statements in main.py: 16
HTTPException raises     : 8
lines in main.py         : 117
```

One file is parsing requests, enforcing rules, writing SQL, managing a transaction, sending e-mail, and building JSON. When a reader wants to know "what are the rules for assignment?", the answer is spread through two functions, mixed with the SQL for audit lines. When a new developer wants to change *how* data is stored, they must edit every route.

### 3.4 The pain log

Write this down. It is the evidence you will use to justify each step, and (in the project in section 19) to document why:

| # | Pain | Evidence | Remedy (section) |
|---|---|---|---|
| P1 | Rule 3 enforced in 1 of 3 entry points | 2 failing tests | Service layer: one place per use case (4) |
| P2 | A failed request corrupts a later one | `test_failed_email_leaves_no_half_saved_task` | Unit of work owns the transaction (7) |
| P3 | Testing one rule needs HTTP + database | measured above | Repository + fake (5, 6), domain model (8) |
| P4 | Rules, SQL, mail and JSON in one block | counts above | Services, repository, domain (4 to 8) |
| P5 | E-mail is sent *inside* the transaction: it can be sent for data that is then rolled back, or lost if the process dies right after commit | reading the code (we will prove it in section 9) | Events and outbox (9) |

Five pains, five remedies, in an order where each step makes the next easier. Notice we found them by **running and measuring**, not by feeling that the code was "messy". That is the habit.

### Try it: write your own pain log

Open your own swe.05 or swe.06 project. Without changing code, find (a) one rule that exists in more than one place (use `grep`), (b) one place where an error in the middle of a request would leave half-saved data, and (c) one test that needs far more set-up than the rule it checks. Write each as a row: pain, evidence, remedy. If you cannot find a row for a layer, you may not need that layer yet.

<details><summary>Answer</summary>

There is no single right answer, but a good row has **evidence you can re-check**: a grep result, a failing test, a timing, a line count. "The code is messy" is not evidence. If your project honestly has none of the three, that is a good result: it means your code is small enough that layers would only cost you. Keep the log; the project (section 19) asks you to refactor only the pain that is really there.

</details>


## 4. Layer 1: the service layer

### 4.1 The pain it removes

**P1: the same rule lives in several routes and drifts apart.** The cause is that the *use cases* ("create a task", "update a task") are written inside the web handlers, and a web handler is a poor home for business rules: it is tied to HTTP, it cannot be called from a command-line script or a background job, and each handler is its own island.

A **service layer** is a set of plain functions, one per **use case**, that hold the application's rules. The web route becomes a translator: it reads the request, calls one service function, and turns the result (or the error) back into an HTTP response.

```text
   before                                  after

   HTTP request                            HTTP request
        |                                       |
   route handler                           route handler        <- parse, call, translate
   (rules + SQL + mail                          |
    + JSON, all mixed)                     service function     <- the rules, one per use case
        |                                       |
   database                                database
```

### 4.2 Rules for a good service function

- **Named after what the user wants**: `create_task`, `update_task`, not `handle_post` or `task_service.process`.
- **No HTTP knowledge**: it never imports FastAPI, never sees a `Request`, never returns a status code. It takes plain values and returns plain values (or raises a **domain error**).
- **Domain errors, not HTTP errors.** A rule violation raises `RuleViolation("assignee already has 3 open tasks")`. The web layer decides this means HTTP 409. Another caller (a CLI) can decide it means "print a message and exit 1".
- **One place for each rule.** If two use cases need the same check, they call the same small helper.
- **It does not commit.** Whoever calls the service decides when the transaction ends (more about this soon).

First the errors, kept in a file of their own so every layer can import them:

```python
# taskboard/errors.py
class DomainError(Exception):
    """A business rule was broken. This is a normal outcome, not a bug."""


class NotFound(DomainError):
    pass


class InvalidInput(DomainError):
    pass


class RuleViolation(DomainError):
    pass
```

Now the service module. The SQL is still here; we only moved the code out of the route and removed the duplication. Compare each function with the old handler:

```python
# taskboard/services.py
from datetime import datetime, timezone

from . import mailer
from .errors import InvalidInput, NotFound, RuleViolation

MAX_OPEN = 3
ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _check_member(conn, project_id, user_id):
    row = conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                       (project_id, user_id)).fetchone()
    if row is None:
        raise RuleViolation("assignee is not a member of this project")


def _check_capacity(conn, user_id):
    """Rule 3, written exactly once."""
    n = conn.execute("SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'",
                     (user_id,)).fetchone()[0]
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
    cur = conn.execute(
        "INSERT INTO tasks (project_id, title, status, assignee_id, created_at) "
        "VALUES (?, ?, 'todo', ?, ?)", (project_id, title, assignee_id, stamp))
    task_id = cur.lastrowid
    conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'created', ?)", (task_id, stamp))
    if assignee_id is not None:
        email = conn.execute("SELECT email FROM users WHERE id = ?", (assignee_id,)).fetchone()[0]
        mailer.send_email(email, f"New task: {title}")
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
            _check_capacity(conn, assignee_id)          # an open task moving to a new person
        conn.execute("UPDATE tasks SET assignee_id = ? WHERE id = ?", (assignee_id, task_id))
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, 'assigned', ?)",
                     (task_id, stamp))
        email = conn.execute("SELECT email FROM users WHERE id = ?", (assignee_id,)).fetchone()[0]
        mailer.send_email(email, f"Task assigned: {task['title']}")
        current_assignee = assignee_id
    if status is not None:
        if (current_status, status) not in ALLOWED:
            raise RuleViolation(f"cannot move from {current_status} to {status}")
        if current_status == "done" and current_assignee is not None:
            _check_capacity(conn, current_assignee)     # reopening makes the task open again
        completed = stamp if status == "done" else None
        conn.execute("UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
                     (status, completed, task_id))
        conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, ?, ?)",
                     (task_id, f"status:{status}", stamp))
    return _task_json(conn, task_id)


def get_task(conn, task_id):
    if conn.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone() is None:
        raise NotFound("task not found")
    return _task_json(conn, task_id)


def list_tasks(conn, project_id, status=None):
    sql, args = "SELECT id FROM tasks WHERE project_id = ?", [project_id]
    if status is not None:
        sql, args = sql + " AND status = ?", args + [status]
    return [_task_json(conn, r["id"]) for r in conn.execute(sql + " ORDER BY id", args).fetchall()]


def _task_json(conn, task_id):
    t = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return {"id": t["id"], "project_id": t["project_id"], "title": t["title"],
            "status": t["status"], "assignee_id": t["assignee_id"],
            "completed_at": t["completed_at"]}
```

Rule 3 now has **one** definition, `_check_capacity`, and three entry points call it (create, assign, reopen). That is the whole fix for P1. Look at the two decisions hidden in `update_task`; they are the kind of detail that a copy-pasted rule gets wrong: the capacity check is *skipped* when the task is already done (assigning a closed task to someone does not make them busier) and when the person is already the assignee (re-assigning to the same person changes nothing).

### 4.3 The thin route

The route file shrinks to a translator. It also gets a small helper, `run`, that owns the transaction for one request: commit if the service finished, roll back if anything raised. This tiny helper alone repairs the second pain (P2: the orphan task after a failed e-mail), because a failed request is now rolled back before the next request can commit it.

```python
# taskboard/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import db, services
from .errors import DomainError, NotFound, InvalidInput, RuleViolation

app = FastAPI(title="Taskboard")

STATUS_FOR = {NotFound: 404, InvalidInput: 422, RuleViolation: 409}


@app.exception_handler(DomainError)
def domain_error_to_http(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=STATUS_FOR.get(type(exc), 400))


class NewTask(BaseModel):
    title: str
    assignee_id: int | None = None


class TaskPatch(BaseModel):
    assignee_id: int | None = None
    status: str | None = None


def run(use_case, *args):
    """Run one use case as one transaction."""
    conn = db.get_conn()
    try:
        result = use_case(conn, *args)
        conn.commit()
        return result
    except Exception:
        conn.rollback()
        raise


@app.post("/projects/{project_id}/tasks", status_code=201)
def create_task(project_id: int, body: NewTask):
    return run(services.create_task, project_id, body.title, body.assignee_id)


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, body: TaskPatch):
    return run(services.update_task, task_id, body.assignee_id, body.status)


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    return run(services.get_task, task_id)


@app.get("/projects/{project_id}/tasks")
def list_tasks(project_id: int, status: str | None = None):
    return run(services.list_tasks, project_id, status)
```

Run **all** tests: the 8 original API tests (behaviour must not change) and the 3 pain tests that failed before:

```bash run
python -m pytest -q -p no:cacheprovider tests
```
```text
...........                                                              [100%]
11 passed in 0.23s
```

All 11 pass, and the original 8 were not edited. That is the refactoring contract: *the outside stayed the same, and two bugs disappeared as a side effect of having one place for the rule*. (Strictly, we changed behaviour on purpose where the old behaviour broke the rules; always do this as a visible step, never hidden inside a "cleanup".)

### 4.4 A second caller: the payoff you can see

The real test of a service layer is whether a **different caller** can use it without HTTP. Here is a command-line "bulk import" that creates tasks, using exactly the same function and therefore exactly the same rules:

```bash run
python - <<'EOF'
import os, sqlite3, tempfile
from taskboard import db, services
from taskboard.errors import DomainError
from taskboard.schema import SCHEMA
from tests.seed import SEED

path = os.path.join(tempfile.mkdtemp(), "cli.db")
os.environ["TASKBOARD_DB"] = path
db.reset()
c = sqlite3.connect(path); c.executescript(SCHEMA + SEED); c.close()

conn = db.get_conn()
rows = [("Plan sprint", 1), ("Fix login", 1), ("Write docs", 1), ("One too many", 1), ("Stranger", 3)]
for title, user in rows:
    try:
        services.create_task(conn, 1, title, user)
        conn.commit()
        print(f"ok       {title!r} -> user {user}")
    except DomainError as e:
        conn.rollback()
        print(f"refused  {title!r}: {e}")
EOF
```
```text
ok       'Plan sprint' -> user 1
ok       'Fix login' -> user 1
ok       'Write docs' -> user 1
refused  'One too many': assignee already has 3 open tasks
refused  'Stranger': assignee is not a member of this project
```

The WIP rule and the membership rule held with no web server in sight.

### 4.5 What the service layer did not fix, and what to avoid

Look at `services.py` again. It still contains SQL, `mailer`, JSON-shaped dictionaries and the transaction is still *global state* (a shared connection). A service layer is the cheapest and most valuable first step, but it is only the first.

Common mistakes with services:

- **A "god service"** called `TaskService` with 40 methods and a `self.db` it never stops using. Prefer small functions grouped by file; a class is fine, but only if it earns its place.
- **Services that return `Response` objects or raise `HTTPException`.** That glues them back to the web.
- **Services that call other services in a loop** until nobody knows where the transaction starts. One use case = one transaction, started at the edge.
- **Pass-through services** whose whole body is `return db.get(x)`. If a use case has no rule, a route may read data directly; do not add a layer for symmetry.

### Try it: add a rule in one place

Add rule 7: "a task title may not contain the word `TODO`" (case-insensitive). Where does the code change? How many tests must you edit?

<details><summary>Answer</summary>

One edit in `create_task` (a check next to the length check), plus a new test. The route needs **no** change, because it only translates; a CLI import would get the rule for free. If you had to edit the route as well, a rule leaked into the web layer. (A rename use case would call the same check; if you add one, move the check into a helper like `_check_title(title)`, which is the same pattern as `_check_capacity`.)

</details>

## 5. Layer 2: the repository

### 5.1 The pain it removes

Open `services.py` and read `update_task` as if you were the product owner. You are trying to find the rules, but every rule is wrapped in SQL: `SELECT 1 FROM members WHERE project_id = ?`. Two problems follow, and you can measure both.

**P3: testing a rule needs a database.** The service takes a `conn`. To test "a 4th open task is refused" you need a real SQLite connection with the right tables and rows. It is fast here (SQLite in memory), but with PostgreSQL in Docker the same test would need a running server, and nobody runs those tests often.

**P4: the rules and the storage details are tangled.** To change how membership is stored (say, a new `roles` table), you must edit the service, and every other service that asked the same question with its own copy of the SQL.

A **repository** is an object that looks like a **collection of domain things** ("the tasks", "the projects") and hides how they are stored. The service asks `tasks.open_count(user_id)`; only the repository knows this is a `SELECT COUNT(*)`.

```text
   service function
        |   asks in business words:  is_member(project, user)? open_count(user)? get(task)?
        v
   repository  (interface: a few methods)
     /      \
  SQLite    fake in memory     <- two implementations, same behaviour
  version   (for fast tests)
```

### 5.2 Design the interface in business words

Do not mirror your tables; mirror your questions. What does the use case need to know?

| The service wants to know | Repository method |
|---|---|
| does this project exist? | `projects.exists(project_id)` |
| is the user a member of the project? | `projects.is_member(project_id, user_id)` |
| how many open tasks does the user have? | `tasks.open_count(user_id)` |
| give me this task | `tasks.get(task_id)` (or `None`) |
| store this new task | `tasks.add(task)` |
| store my changes to this task | `tasks.save(task)` |
| list the tasks of a project | `tasks.list(project_id, status=None)` |
| record an audit line | `tasks.add_audit(task_id, action, at)` |
| where do I send the mail? | `users.email_of(user_id)` |

Three small repositories (tasks, projects, users) are bundled in one `Repos` object that services receive. The service no longer sees SQL, rows, or connections.

First a plain `Task` object, so the repository returns *a thing* and not a database row. For now it is just data:

```python
# taskboard/domain.py
from dataclasses import dataclass


@dataclass
class Task:
    id: int | None
    project_id: int
    title: str
    status: str
    assignee_id: int | None
    created_at: str
    completed_at: str | None = None
```

Now the SQLite repositories. **All SQL in the program is now in this one file** (except the schema):

```python
# taskboard/repo.py
from .domain import Task


def _task(row):
    return Task(id=row["id"], project_id=row["project_id"], title=row["title"],
                status=row["status"], assignee_id=row["assignee_id"],
                created_at=row["created_at"], completed_at=row["completed_at"])


class SqliteTaskRepo:
    def __init__(self, conn):
        self.conn = conn

    def get(self, task_id):
        row = self.conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return _task(row) if row else None

    def add(self, task):
        cur = self.conn.execute(
            "INSERT INTO tasks (project_id, title, status, assignee_id, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (task.project_id, task.title, task.status, task.assignee_id, task.created_at))
        task.id = cur.lastrowid
        return task

    def save(self, task):
        self.conn.execute(
            "UPDATE tasks SET title = ?, status = ?, assignee_id = ?, completed_at = ? WHERE id = ?",
            (task.title, task.status, task.assignee_id, task.completed_at, task.id))

    def list(self, project_id, status=None):
        sql, args = "SELECT * FROM tasks WHERE project_id = ?", [project_id]
        if status is not None:
            sql, args = sql + " AND status = ?", args + [status]
        return [_task(r) for r in self.conn.execute(sql + " ORDER BY id", args).fetchall()]

    def open_count(self, user_id):
        return self.conn.execute(
            "SELECT COUNT(*) FROM tasks WHERE assignee_id = ? AND status != 'done'",
            (user_id,)).fetchone()[0]

    def add_audit(self, task_id, action, at):
        self.conn.execute("INSERT INTO audit (task_id, action, at) VALUES (?, ?, ?)",
                          (task_id, action, at))

    def audit_for(self, task_id):
        rows = self.conn.execute("SELECT action FROM audit WHERE task_id = ? ORDER BY id",
                                 (task_id,)).fetchall()
        return [r["action"] for r in rows]


class SqliteProjectRepo:
    def __init__(self, conn):
        self.conn = conn

    def exists(self, project_id):
        return self.conn.execute("SELECT 1 FROM projects WHERE id = ?",
                                 (project_id,)).fetchone() is not None

    def is_member(self, project_id, user_id):
        return self.conn.execute("SELECT 1 FROM members WHERE project_id = ? AND user_id = ?",
                                 (project_id, user_id)).fetchone() is not None


class SqliteUserRepo:
    def __init__(self, conn):
        self.conn = conn

    def email_of(self, user_id):
        return self.conn.execute("SELECT email FROM users WHERE id = ?", (user_id,)).fetchone()[0]


class SqliteRepos:
    """The bundle that services receive."""
    def __init__(self, conn):
        self.tasks = SqliteTaskRepo(conn)
        self.projects = SqliteProjectRepo(conn)
        self.users = SqliteUserRepo(conn)
```

### 5.3 The service, rewritten to ask in business words

The same use cases; compare them with section 4. There is no `SELECT` anywhere, and each function reads like the rules from section 2.1:

```python
# taskboard/services.py
from datetime import datetime, timezone

from . import mailer
from .domain import Task
from .errors import InvalidInput, NotFound, RuleViolation

MAX_OPEN = 3
ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _check_member(repos, project_id, user_id):
    if not repos.projects.is_member(project_id, user_id):
        raise RuleViolation("assignee is not a member of this project")


def _check_capacity(repos, user_id):
    if repos.tasks.open_count(user_id) >= MAX_OPEN:
        raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")


def create_task(repos, project_id, title, assignee_id=None):
    title = title.strip()
    if not title or len(title) > 120:
        raise InvalidInput("title must have 1 to 120 characters")
    if not repos.projects.exists(project_id):
        raise NotFound("project not found")
    if assignee_id is not None:
        _check_member(repos, project_id, assignee_id)
        _check_capacity(repos, assignee_id)
    task = repos.tasks.add(Task(None, project_id, title, "todo", assignee_id, _now()))
    repos.tasks.add_audit(task.id, "created", task.created_at)
    if assignee_id is not None:
        mailer.send_email(repos.users.email_of(assignee_id), f"New task: {title}")
    return task


def update_task(repos, task_id, assignee_id=None, status=None):
    task = repos.tasks.get(task_id)
    if task is None:
        raise NotFound("task not found")
    stamp = _now()
    if assignee_id is not None:
        _check_member(repos, task.project_id, assignee_id)
        if task.status != "done" and assignee_id != task.assignee_id:
            _check_capacity(repos, assignee_id)         # an open task moving to a new person
        task.assignee_id = assignee_id
        repos.tasks.add_audit(task.id, "assigned", stamp)
        mailer.send_email(repos.users.email_of(assignee_id), f"Task assigned: {task.title}")
    if status is not None:
        if (task.status, status) not in ALLOWED:
            raise RuleViolation(f"cannot move from {task.status} to {status}")
        if task.status == "done" and task.assignee_id is not None:
            _check_capacity(repos, task.assignee_id)    # reopening makes the task open again
        task.status = status
        task.completed_at = stamp if status == "done" else None
        repos.tasks.add_audit(task.id, f"status:{status}", stamp)
    repos.tasks.save(task)
    return task


def get_task(repos, task_id):
    task = repos.tasks.get(task_id)
    if task is None:
        raise NotFound("task not found")
    return task


def list_tasks(repos, project_id, status=None):
    return repos.tasks.list(project_id, status)
```

The route changes in two places: `run` builds the repositories, and a small function turns a `Task` into JSON:

```diff
# taskboard/main.py
- from . import db, services
- from .errors import DomainError, NotFound, InvalidInput, RuleViolation
+ from . import db, services
+ from .errors import DomainError, NotFound, InvalidInput, RuleViolation
+ from .repo import SqliteRepos
```

```diff
# taskboard/main.py
-         result = use_case(conn, *args)
-         conn.commit()
-         return result
+         result = use_case(SqliteRepos(conn), *args)
+         conn.commit()
+         return result
```

```diff
# taskboard/main.py
- @app.post("/projects/{project_id}/tasks", status_code=201)
- def create_task(project_id: int, body: NewTask):
-     return run(services.create_task, project_id, body.title, body.assignee_id)
-
-
- @app.patch("/tasks/{task_id}")
- def update_task(task_id: int, body: TaskPatch):
-     return run(services.update_task, task_id, body.assignee_id, body.status)
-
-
- @app.get("/tasks/{task_id}")
- def get_task(task_id: int):
-     return run(services.get_task, task_id)
-
-
- @app.get("/projects/{project_id}/tasks")
- def list_tasks(project_id: int, status: str | None = None):
-     return run(services.list_tasks, project_id, status)
+ def task_json(t):
+     return {"id": t.id, "project_id": t.project_id, "title": t.title, "status": t.status,
+             "assignee_id": t.assignee_id, "completed_at": t.completed_at}
+
+
+ @app.post("/projects/{project_id}/tasks", status_code=201)
+ def create_task(project_id: int, body: NewTask):
+     return task_json(run(services.create_task, project_id, body.title, body.assignee_id))
+
+
+ @app.patch("/tasks/{task_id}")
+ def update_task(task_id: int, body: TaskPatch):
+     return task_json(run(services.update_task, task_id, body.assignee_id, body.status))
+
+
+ @app.get("/tasks/{task_id}")
+ def get_task(task_id: int):
+     return task_json(run(services.get_task, task_id))
+
+
+ @app.get("/projects/{project_id}/tasks")
+ def list_tasks(project_id: int, status: str | None = None):
+     return [task_json(t) for t in run(services.list_tasks, project_id, status)]
```

Behaviour must be identical:

```bash run
python -m pytest -q -p no:cacheprovider tests
```
```text
...........                                                              [100%]
11 passed in 0.22s
```

Still 11 passing, and the API tests were again not touched.

## 6. Fakes, contract tests, and what a repository really buys you

### 6.1 A fake repository

Now the payoff for P3. A **fake** is a simple, in-memory implementation of the same interface. It is not a mock that records calls: it is a small working version that *behaves* like the real thing. Because the services only use the repository's methods, we can hand them the fake and test every rule without SQL, files or web servers.

The test world (`tests/seed.py` from section 2.3) exists as SQL. The fakes need the same people and projects as plain Python, so we write that down once. The fakes keep their state in one plain dictionary, `data`; we reuse that design in section 7:

```python
# tests/fakes.py
import copy
import sqlite3

from seed import SEED
from taskboard.repo import SqliteRepos
from taskboard.schema import SCHEMA


def world_data():
    """The same people and projects as SEED, as plain Python."""
    return {
        "tasks": {}, "audit": [], "next_id": 1,
        "users": {1: "ana@example.com", 2: "ben@example.com",
                  3: "cy@example.com", 4: "bounce@example.com"},
        "projects": {1, 2},
        "members": {(1, 1), (1, 2), (1, 4), (2, 3)},
    }


class FakeTaskRepo:
    def __init__(self, data):
        self.data = data

    # Copies in and out: a real database hands you a *new* object every time.
    def get(self, task_id):
        t = self.data["tasks"].get(task_id)
        return copy.copy(t) if t else None

    def add(self, task):
        task.id = self.data["next_id"]
        self.data["next_id"] += 1
        self.data["tasks"][task.id] = copy.copy(task)
        return task

    def save(self, task):
        self.data["tasks"][task.id] = copy.copy(task)

    def list(self, project_id, status=None):
        rows = sorted(self.data["tasks"].values(), key=lambda t: t.id)
        return [copy.copy(t) for t in rows
                if t.project_id == project_id and (status is None or t.status == status)]

    def open_count(self, user_id):
        return sum(1 for t in self.data["tasks"].values()
                   if t.assignee_id == user_id and t.status != "done")

    def add_audit(self, task_id, action, at):
        self.data["audit"].append((task_id, action))

    def audit_for(self, task_id):
        return [a for tid, a in self.data["audit"] if tid == task_id]


class FakeProjectRepo:
    def __init__(self, data):
        self.data = data

    def exists(self, project_id):
        return project_id in self.data["projects"]

    def is_member(self, project_id, user_id):
        return (project_id, user_id) in self.data["members"]


class FakeUserRepo:
    def __init__(self, data):
        self.data = data

    def email_of(self, user_id):
        return self.data["users"][user_id]


class FakeRepos:
    def __init__(self, data):
        self.tasks = FakeTaskRepo(data)
        self.projects = FakeProjectRepo(data)
        self.users = FakeUserRepo(data)


def fake_world():
    return FakeRepos(world_data())


def sqlite_world():
    """The real SQL repositories on a throw-away in-memory database."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA + SEED)
    return SqliteRepos(conn)
```

### 6.2 Unit tests of the rules, without a database

```python
# tests/test_services_unit.py
import pytest

from fakes import fake_world
from taskboard import mailer, services
from taskboard.errors import InvalidInput, NotFound, RuleViolation


@pytest.fixture(autouse=True)
def quiet_mailer():
    mailer.SENT.clear()      # services still call the global mailer (we fix that in section 9)


def test_fourth_open_task_is_refused():
    repos = fake_world()
    for i in range(3):
        services.create_task(repos, 1, f"t{i}", assignee_id=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        services.create_task(repos, 1, "t3", assignee_id=1)


def test_assigning_an_existing_task_respects_the_limit():
    repos = fake_world()
    for i in range(3):
        services.create_task(repos, 1, f"t{i}", assignee_id=1)
    loose = services.create_task(repos, 1, "loose")
    with pytest.raises(RuleViolation, match="3 open tasks"):
        services.update_task(repos, loose.id, assignee_id=1)


def test_reopening_respects_the_limit():
    repos = fake_world()
    old = services.create_task(repos, 1, "old", assignee_id=1)
    services.update_task(repos, old.id, status="doing")
    services.update_task(repos, old.id, status="done")
    for i in range(3):
        services.create_task(repos, 1, f"t{i}", assignee_id=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        services.update_task(repos, old.id, status="todo")


def test_done_tasks_do_not_count_as_open():
    repos = fake_world()
    first = services.create_task(repos, 1, "first", assignee_id=1)
    services.update_task(repos, first.id, status="doing")
    services.update_task(repos, first.id, status="done")
    for i in range(3):
        services.create_task(repos, 1, f"t{i}", assignee_id=1)      # 3 open + 1 done: fine


def test_reassigning_to_the_same_person_is_not_a_new_load():
    repos = fake_world()
    tasks = [services.create_task(repos, 1, f"t{i}", assignee_id=1) for i in range(3)]
    services.update_task(repos, tasks[0].id, assignee_id=1)         # no error


def test_title_rules_and_missing_project():
    repos = fake_world()
    assert services.create_task(repos, 1, "  padded  ").title == "padded"
    with pytest.raises(InvalidInput):
        services.create_task(repos, 1, "   ")
    with pytest.raises(NotFound):
        services.create_task(repos, 99, "x")


def test_audit_trail_has_one_line_per_change():
    repos = fake_world()
    t = services.create_task(repos, 1, "x", assignee_id=2)
    services.update_task(repos, t.id, status="doing")
    assert repos.tasks.audit_for(t.id) == ["created", "status:doing"]
```

```bash run
python -m pytest -q -p no:cacheprovider tests/test_services_unit.py
```
```text
.......                                                                  [100%]
7 passed in 0.08s
```

Seven rule tests, no HTTP, no files, no schema. When one fails the error points at a rule, not at a status code. Compare the speed of the three ways to run the same use case (numbers depend on your machine; the ratio is the lesson):

```bash run
python - <<'EOF'
import sys, time
sys.path.insert(0, "tests")
from fakes import fake_world, sqlite_world
from taskboard import services

def per_call(make_repos, n=2000):
    repos = make_repos()
    start = time.perf_counter()
    for i in range(n):
        services.create_task(repos, 1, f"t{i}")
    return (time.perf_counter() - start) / n * 1000

print(f"service + fake repositories   : {per_call(fake_world):.4f} ms per create")
print(f"service + SQLite in memory    : {per_call(sqlite_world):.4f} ms per create")
print("service + HTTP + SQLite file  : several ms per create (measured in section 3.2)")
EOF
```
```text
service + fake repositories   : 0.0037 ms per create
service + SQLite in memory    : 0.0042 ms per create
service + HTTP + SQLite file  : several ms per create (measured in section 3.2)
```

The fake is the fastest, and the in-memory SQLite is also very fast; it is the HTTP stack that costs the most. This is an honest result worth remembering: **for SQLite, the in-memory database is already a very good test double**. The fake earns its keep when the real database is slow to start (PostgreSQL, a remote service) or when you want to control failures that are hard to trigger in SQL.

### 6.3 Fakes can lie: contract tests

A fake is code, and code has bugs. If the fake behaves differently from the real repository, your fast tests pass while production fails. Here is the classic way a fake lies. A real database returns a **new** object on each `get`, so a service that changes the object and forgets to call `save` loses the change. A lazy fake that returns the *same* object hides this bug:

```bash run
python - <<'EOF'
import sys
sys.path.insert(0, "tests")
from fakes import FakeTaskRepo, fake_world, sqlite_world
from taskboard.domain import Task

class LazyTaskRepo(FakeTaskRepo):          # no copying: the "obvious" way to write a fake
    def get(self, task_id):
        return self.data["tasks"].get(task_id)
    def add(self, task):
        task.id = self.data["next_id"]; self.data["next_id"] += 1
        self.data["tasks"][task.id] = task
        return task

def rename_but_forget_to_save(repos, task_id, title):      # BUG: no repos.tasks.save(task)
    task = repos.tasks.get(task_id)
    task.title = title

for name, repos in [("lazy fake", fake_world()), ("careful fake", fake_world()), ("real SQLite", sqlite_world())]:
    if name == "lazy fake":
        repos.tasks = LazyTaskRepo(repos.tasks.data)
    t = repos.tasks.add(Task(None, 1, "old title", "todo", None, "now"))
    rename_but_forget_to_save(repos, t.id, "new title")
    print(f"{name:13}: title afterwards = {repos.tasks.get(t.id).title!r}")
EOF
```
```text
lazy fake    : title afterwards = 'new title'
careful fake : title afterwards = 'old title'
real SQLite  : title afterwards = 'old title'
```

Only the lazy fake says `'new title'`; a test written against it would pass and hide the bug. The careful fake and real SQLite both say `'old title'`, which is the truth. To stop fakes from drifting, write **contract tests**: one set of tests for the repository interface that runs against *every* implementation. If the fake and the SQL version both pass the same tests, they agree.

```python
# tests/test_repo_contract.py
import pytest

from fakes import fake_world, sqlite_world
from taskboard.domain import Task


@pytest.fixture(params=["fake", "sqlite"])
def repos(request):
    return fake_world() if request.param == "fake" else sqlite_world()


def new_task(**kw):
    base = dict(id=None, project_id=1, title="t", status="todo", assignee_id=None,
                created_at="2026-01-01T00:00:00")
    return Task(**{**base, **kw})


def test_add_assigns_an_id_and_get_returns_equal_data(repos):
    t = repos.tasks.add(new_task(title="hello"))
    assert t.id is not None, "add must set the id on the object"
    assert repos.tasks.get(t.id) == t


def test_get_unknown_is_none(repos):
    assert repos.tasks.get(12345) is None, "a missing task is None, not an exception"


def test_changes_are_lost_without_save(repos):
    t = repos.tasks.add(new_task(title="old"))
    again = repos.tasks.get(t.id)
    again.title = "changed but not saved"
    assert repos.tasks.get(t.id).title == "old", "get must return a new object each time"


def test_save_persists_changes(repos):
    t = repos.tasks.add(new_task())
    t.status, t.completed_at = "done", "2026-02-02T00:00:00"
    repos.tasks.save(t)
    assert repos.tasks.get(t.id).status == "done"
    assert repos.tasks.get(t.id).completed_at == "2026-02-02T00:00:00"


def test_list_is_ordered_and_filtered(repos):
    a = repos.tasks.add(new_task(title="a", status="doing"))
    b = repos.tasks.add(new_task(title="b"))
    repos.tasks.add(new_task(title="elsewhere", project_id=2))
    assert [t.id for t in repos.tasks.list(1)] == [a.id, b.id]
    assert [t.id for t in repos.tasks.list(1, "doing")] == [a.id]


def test_open_count_ignores_done_and_other_people(repos):
    repos.tasks.add(new_task(assignee_id=1))
    repos.tasks.add(new_task(assignee_id=1, status="doing"))
    repos.tasks.add(new_task(assignee_id=1, status="done"))
    repos.tasks.add(new_task(assignee_id=2))
    repos.tasks.add(new_task(assignee_id=None))
    assert repos.tasks.open_count(1) == 2, "only non-done tasks of that user"


def test_projects_and_users(repos):
    assert repos.projects.exists(1) and not repos.projects.exists(99)
    assert repos.projects.is_member(1, 1) and not repos.projects.is_member(1, 3)
    assert repos.users.email_of(2) == "ben@example.com"


def test_audit_lines_keep_their_order(repos):
    t = repos.tasks.add(new_task())
    repos.tasks.add_audit(t.id, "created", "x")
    repos.tasks.add_audit(t.id, "assigned", "y")
    assert repos.tasks.audit_for(t.id) == ["created", "assigned"]
```

```bash run
python -m pytest -q -p no:cacheprovider tests/test_repo_contract.py tests/test_services_unit.py tests/test_api.py tests/test_pain.py
```
```text
..................................                                       [100%]
34 passed in 0.24s
```

Eight contract tests ran twice (16 results), once per implementation, plus the unit and API tests. The whole safety net still passes.

### 6.4 So what did the repository buy us? An honest list

| Claim | True here? | Evidence |
|---|---|---|
| "I can test rules without a database" | Yes | 7 unit tests, no SQL, no fixture file |
| "I can switch to PostgreSQL by writing one class" | Partly | The SQL is in one file now, so the *work* is localised. But you still must write and test every method, and SQL dialects differ. |
| "Services read like the rules" | Yes | Compare `update_task` in section 4 and 5 |
| "Faster tests" | Only a little with SQLite | In-memory SQLite is already fast. The fake wins when the real database is slow. |
| "It is free" | No | 1 new file of 90 lines, 1 fake of 80 lines, 1 contract test, and a mapping function |

**Answer to the outcome question "what concrete pain does a repository remove in your project?"** is therefore: *SQL scattered through rule code (P4), and tests that need a database (P3)*. Not "it is the correct architecture". If neither pain is present in your own project, the honest answer is that you do not need one yet.

### Try it: the repository for a one-table app

An app has one table `notes(id, text)` and three routes: create, read, delete. There are no rules. Would you add a `NoteRepository` and a `NoteService`? Write the three-line argument for or against.

<details><summary>Answer</summary>

**No.** There are no rules for a service to hold (P1 absent), the SQL is three one-line statements (P4 is a non-problem), and testing through the route plus a temp database is easy. The repository would be a mapping layer with nothing to protect. Add it when a rule appears (for example "a user may have at most 100 notes") or when the same query is copied into several routes. Layers are a response to pain, so no pain, no layer.

</details>

## 7. Layer 3: the unit of work

### 7.1 The pain it removes

The `run` helper in section 4 fixed the orphan-task bug. Is the transaction handling therefore solved? Not quite. The shared connection (`db.get_conn()`) is still **one connection for the whole process**, and a web server handles many requests at the same time. Imagine two requests interleaved on one connection:

```bash run
python - <<'EOF'
import os, sqlite3, tempfile
path = os.path.join(tempfile.mkdtemp(), "shared.db")
shared = sqlite3.connect(path)
shared.execute("CREATE TABLE t (name TEXT)")
shared.commit()

shared.execute("INSERT INTO t VALUES ('request A: important work')")    # A is half-way through
shared.execute("INSERT INTO t VALUES ('request B: doomed')")            # B starts on the same connection...
shared.rollback()                                                        # ...and fails: rolls back EVERYTHING pending
shared.commit()                                                          # A finishes and commits

print("rows in the database:", sqlite3.connect(path).execute("SELECT name FROM t").fetchall())
EOF
```
```text
rows in the database: []
```

Request A's work is **gone** because request B rolled back the connection they shared. (In the real app the effect is rarer, since the threadpool serialises some work, but it is a bug waiting for the day traffic is high; it also shows how `check_same_thread=False` hides a design error.) The cure is simple to state: **every use case gets its own connection, and one object owns its transaction from start to finish**. That object is the **unit of work**.

A **unit of work** (UoW) does four things:

1. **Opens** a connection (or session) at the start of the use case.
2. **Provides** the repositories, all bound to that same connection, so they share one transaction.
3. **Commits** when the service says so (`uow.commit()`).
4. **Rolls back and closes** at the end if no commit happened, including when an exception flies out.

In Python, this is a **context manager**:

```python
with uow:                      # open, hand out repos
    task = uow.tasks.get(7)
    ...
    uow.commit()               # make it permanent
# leaving the block: rollback if commit was not called, then close
```

### 7.2 The SQLite unit of work

The database module loses its global; it only knows how to open a configured connection:

```python
# taskboard/db.py
import sqlite3

from .schema import SCHEMA


def connect(path):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
```

```python
# taskboard/uow.py
from .db import connect
from .repo import SqliteRepos


class SqliteUnitOfWork:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        self.conn = connect(self.path)
        repos = SqliteRepos(self.conn)
        self.tasks, self.projects, self.users = repos.tasks, repos.projects, repos.users
        return self

    def __exit__(self, exc_type, exc, tb):
        self.conn.rollback()        # no-op if commit() was called; undoes everything otherwise
        self.conn.close()

    def commit(self):
        self.conn.commit()
```

Four lines of logic. Notice that `__exit__` **always** calls `rollback()`: after a commit it does nothing, and after a failure it undoes the work. A forgotten `commit()` can never leave half a change behind; the worst that can happen is that nothing is saved, which a test will notice at once.

### 7.3 The services take a unit of work

Each use case now begins with `with uow:`. Only the commit points and the parameter name change; the rules stay exactly as they were:

```python
# taskboard/services.py
from datetime import datetime, timezone

from . import mailer
from .domain import Task
from .errors import InvalidInput, NotFound, RuleViolation

MAX_OPEN = 3
ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}


def _now():
    return datetime.now(timezone.utc).isoformat()


def _check_member(uow, project_id, user_id):
    if not uow.projects.is_member(project_id, user_id):
        raise RuleViolation("assignee is not a member of this project")


def _check_capacity(uow, user_id):
    if uow.tasks.open_count(user_id) >= MAX_OPEN:
        raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")


def create_task(uow, project_id, title, assignee_id=None):
    title = title.strip()
    if not title or len(title) > 120:
        raise InvalidInput("title must have 1 to 120 characters")
    with uow:
        if not uow.projects.exists(project_id):
            raise NotFound("project not found")
        if assignee_id is not None:
            _check_member(uow, project_id, assignee_id)
            _check_capacity(uow, assignee_id)
        task = uow.tasks.add(Task(None, project_id, title, "todo", assignee_id, _now()))
        uow.tasks.add_audit(task.id, "created", task.created_at)
        if assignee_id is not None:
            mailer.send_email(uow.users.email_of(assignee_id), f"New task: {title}")
        uow.commit()
        return task


def update_task(uow, task_id, assignee_id=None, status=None):
    with uow:
        task = uow.tasks.get(task_id)
        if task is None:
            raise NotFound("task not found")
        stamp = _now()
        if assignee_id is not None:
            _check_member(uow, task.project_id, assignee_id)
            if task.status != "done" and assignee_id != task.assignee_id:
                _check_capacity(uow, assignee_id)
            task.assignee_id = assignee_id
            uow.tasks.add_audit(task.id, "assigned", stamp)
            mailer.send_email(uow.users.email_of(assignee_id), f"Task assigned: {task.title}")
        if status is not None:
            if (task.status, status) not in ALLOWED:
                raise RuleViolation(f"cannot move from {task.status} to {status}")
            if task.status == "done" and task.assignee_id is not None:
                _check_capacity(uow, task.assignee_id)
            task.status = status
            task.completed_at = stamp if status == "done" else None
            uow.tasks.add_audit(task.id, f"status:{status}", stamp)
        uow.tasks.save(task)
        uow.commit()
        return task


def get_task(uow, task_id):
    with uow:
        task = uow.tasks.get(task_id)
        if task is None:
            raise NotFound("task not found")
        return task


def list_tasks(uow, project_id, status=None):
    with uow:
        return uow.tasks.list(project_id, status)
```

The route no longer needs `run`: the service owns its transaction. A function `new_uow()` builds a fresh unit of work (and therefore a fresh connection) for each request:

```diff
# taskboard/main.py
- from . import db, services
- from .errors import DomainError, NotFound, InvalidInput, RuleViolation
- from .repo import SqliteRepos
+ import os
+
+ from . import services
+ from .errors import DomainError, NotFound, InvalidInput, RuleViolation
+ from .uow import SqliteUnitOfWork
```

```diff
# taskboard/main.py
- def run(use_case, *args):
-     """Run one use case as one transaction."""
-     conn = db.get_conn()
-     try:
-         result = use_case(SqliteRepos(conn), *args)
-         conn.commit()
-         return result
-     except Exception:
-         conn.rollback()
-         raise
+ def run(use_case, *args):
+     """Run one use case with a fresh unit of work (its own connection and transaction)."""
+     return use_case(SqliteUnitOfWork(os.environ.get("TASKBOARD_DB", "taskboard.db")), *args)
```

The tests lose the line that reset the old global connection:

```diff
# tests/conftest.py
- from taskboard import db, mailer, main
+ from taskboard import mailer, main
```

```diff
# tests/conftest.py
-     db.reset()
-     mailer.SENT.clear()
+     mailer.SENT.clear()
```

```diff
# tests/conftest.py
-     yield TestClient(main.app, raise_server_exceptions=False)
-     db.reset()
+     yield TestClient(main.app, raise_server_exceptions=False)
```

The service unit tests now need a **fake unit of work**. It must do something clever: behave like a transaction. It copies the data at the start, lets the service change the copy, and only writes it back on `commit()`. If the service fails, the copy is thrown away, exactly like a rollback:

```python
# tests/fake_uow.py
import copy

from fakes import FakeProjectRepo, FakeTaskRepo, FakeUserRepo, world_data


class FakeStore:
    """The 'database': what survives between units of work."""
    def __init__(self):
        self.data = world_data()


class FakeUnitOfWork:
    def __init__(self, store):
        self.store = store
        self.committed = False

    def __enter__(self):
        self.work = copy.deepcopy(self.store.data)      # a private copy = our transaction
        self.tasks = FakeTaskRepo(self.work)
        self.projects = FakeProjectRepo(self.work)
        self.users = FakeUserRepo(self.work)
        return self

    def __exit__(self, exc_type, exc, tb):
        pass                                            # not committed -> the copy is dropped

    def commit(self):
        self.store.data = self.work
        self.committed = True


def fresh():
    """A store plus a function that makes a new unit of work for each call, like main.run does."""
    store = FakeStore()
    return store, (lambda: FakeUnitOfWork(store))
```

Switch the unit tests from `repos` to units of work (each service call gets a fresh `uow()`), and add the two tests that were impossible before: **a failed use case leaves nothing behind**, and **nothing is saved unless the service committed**.

```python
# tests/test_services_unit.py
import pytest

from fake_uow import fresh
from taskboard import mailer, services
from taskboard.domain import Task
from taskboard.errors import InvalidInput, NotFound, RuleViolation


@pytest.fixture(autouse=True)
def quiet_mailer():
    mailer.SENT.clear()      # services still call the global mailer (we fix that in section 9)


@pytest.fixture
def world():
    store, uow = fresh()
    return store, uow


def test_fourth_open_task_is_refused(world):
    store, uow = world
    for i in range(3):
        services.create_task(uow(), 1, f"t{i}", assignee_id=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        services.create_task(uow(), 1, "t3", assignee_id=1)


def test_assigning_an_existing_task_respects_the_limit(world):
    store, uow = world
    for i in range(3):
        services.create_task(uow(), 1, f"t{i}", assignee_id=1)
    loose = services.create_task(uow(), 1, "loose")
    with pytest.raises(RuleViolation, match="3 open tasks"):
        services.update_task(uow(), loose.id, assignee_id=1)


def test_reopening_respects_the_limit(world):
    store, uow = world
    old = services.create_task(uow(), 1, "old", assignee_id=1)
    services.update_task(uow(), old.id, status="doing")
    services.update_task(uow(), old.id, status="done")
    for i in range(3):
        services.create_task(uow(), 1, f"t{i}", assignee_id=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        services.update_task(uow(), old.id, status="todo")


def test_done_tasks_do_not_count_as_open(world):
    store, uow = world
    first = services.create_task(uow(), 1, "first", assignee_id=1)
    services.update_task(uow(), first.id, status="doing")
    services.update_task(uow(), first.id, status="done")
    for i in range(3):
        services.create_task(uow(), 1, f"t{i}", assignee_id=1)      # 3 open + 1 done: fine


def test_reassigning_to_the_same_person_is_not_a_new_load(world):
    store, uow = world
    tasks = [services.create_task(uow(), 1, f"t{i}", assignee_id=1) for i in range(3)]
    services.update_task(uow(), tasks[0].id, assignee_id=1)         # no error


def test_title_rules_and_missing_project(world):
    store, uow = world
    assert services.create_task(uow(), 1, "  padded  ").title == "padded"
    with pytest.raises(InvalidInput):
        services.create_task(uow(), 1, "   ")
    with pytest.raises(NotFound):
        services.create_task(uow(), 99, "x")


def test_audit_trail_has_one_line_per_change(world):
    store, uow = world
    t = services.create_task(uow(), 1, "x", assignee_id=2)
    services.update_task(uow(), t.id, status="doing")
    with uow() as check:
        assert check.tasks.audit_for(t.id) == ["created", "status:doing"]


def test_a_failed_use_case_saves_nothing(world):
    store, uow = world
    t = services.create_task(uow(), 1, "x")
    # assign to Ben (fine), then ask for an illegal move (todo -> done): the whole request fails
    with pytest.raises(RuleViolation):
        services.update_task(uow(), t.id, assignee_id=2, status="done")
    with uow() as check:
        assert check.tasks.get(t.id).assignee_id is None, "the assignment must be rolled back too"
        assert check.tasks.audit_for(t.id) == ["created"], "no audit line for a rolled-back change"


def test_without_commit_nothing_is_kept(world):
    store, uow = world
    unit = uow()
    with unit:
        unit.tasks.add(Task(None, 1, "ghost", "todo", None, "now"))
    assert not unit.committed
    with uow() as check:
        assert check.tasks.list(1) == [], "a forgotten commit must leave no trace"
```

```bash run
python -m pytest -q -p no:cacheprovider tests
```
```text
....................................                                     [100%]
36 passed in 0.27s
```

Everything passes: the HTTP safety net (only the fixture lost two lines), the contract tests, and the unit tests, including the two new transaction tests.

### 7.4 What the unit of work bought us

| Pain | Fixed by | Evidence |
|---|---|---|
| P2 failed request leaves traces | `__exit__` always rolls back | `test_a_failed_use_case_saves_nothing` runs in microseconds, without a database |
| Requests interfering through one shared connection | one connection per use case | `main.run` builds a new unit of work for every request |
| The transaction was a convention ("call `run`") | the transaction is an object | you cannot forget it: the service must say `with uow:` |

Costs: one more class (14 lines), one fake with a deep copy (copying is fine for tests, not for production), and the rule "a service function must open `with uow:` and call `commit()` itself". If a service forgets `commit()`, the failure is immediate: nothing is saved.

**A word on SQLAlchemy and Django.** If you use SQLAlchemy, its `Session` already *is* a unit of work (it tracks changes and commits them together), and a `Repository` over a `Session` is often thin. Django's ORM plus `transaction.atomic()` plays the same role. You do not need to reinvent this machinery in a real project, but you must understand the pattern to use the tools well. We built it by hand once so nothing is magic.

### Try it: where does the commit belong?

A teammate puts `uow.commit()` inside the repository's `add()` method "so that callers cannot forget". What goes wrong?

<details><summary>Answer</summary>

The transaction can no longer span more than one write. `create_task` writes the task, then an audit line, then maybe an outbox row (section 9). With a commit inside `add`, the task is saved before the audit line; a crash in between leaves a task with no audit trail, and the "all or nothing" guarantee, the entire point of the unit of work, is gone. The **use case** knows where it ends, so the use case (the service) calls `commit()` once, at the very end.

</details>


## 8. The domain model: rules live with the data they protect

### 8.1 The pain it removes

Read `update_task` once more. It mixes two kinds of code:

- **Orchestration**: load the task, open the transaction, save, write the audit line, send mail.
- **Rules**: "a done task does not count as open", "a reopened task needs a free slot", "only certain status moves are allowed".

The rules are about the **task itself**: its status, its assignee. They are scattered in the service, next to storage calls, so you cannot test them without a unit of work, and a new developer cannot find "everything a Task is allowed to do" in one place.

A **domain model** puts the rules into the objects. `Task` stops being a bag of fields and gains **behaviour**: methods that change its state and refuse changes that break a rule. The service becomes a short director: fetch the facts, tell the task to change, save.

```text
   service (orchestration)                     domain (rules)
   ------------------------                    ------------------------
   open transaction                            Task.assign(user, is_member, open_count)
   load task, load facts   ---- calls ---->    Task.change_status(new, now, ...)
   save, publish, commit                       raises RuleViolation if a rule breaks
```

### 8.2 The key design question: where do the facts come from?

"A user may have at most 3 open tasks" is a rule about the *task*, but the number of open tasks of a user is a fact that lives in the *database*. A domain object must not call the database (it would drag SQL back in). The simple, honest solution is to **pass the facts in as plain arguments**: the service looks up `open_count` and `is_member`, and the task decides.

```python
task.assign(user_id, is_member=True, open_count=2)
```

This keeps the domain code **pure**: ordinary Python, no I/O, no imports from other layers. Pure code is the easiest code to test.

### 8.3 The domain module

```python
# taskboard/domain.py
from dataclasses import dataclass

from .errors import InvalidInput, RuleViolation

MAX_OPEN = 3
ALLOWED = {("todo", "doing"), ("doing", "todo"), ("doing", "done"), ("done", "todo")}


@dataclass
class Task:
    id: int | None
    project_id: int
    title: str
    status: str
    assignee_id: int | None
    created_at: str
    completed_at: str | None = None

    @classmethod
    def new(cls, project_id, title, now):
        """Rule 1: a title has 1 to 120 characters after trimming."""
        title = title.strip()
        if not title or len(title) > 120:
            raise InvalidInput("title must have 1 to 120 characters")
        return cls(None, project_id, title, "todo", None, now)

    @property
    def is_open(self):
        return self.status != "done"

    def assign(self, user_id, *, is_member, open_count):
        """Rules 2 and 3. `is_member` and `open_count` are facts the caller looked up."""
        if not is_member:
            raise RuleViolation("assignee is not a member of this project")
        if self.is_open and user_id != self.assignee_id and open_count >= MAX_OPEN:
            raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")
        self.assignee_id = user_id

    def change_status(self, new_status, now, *, assignee_open_count=0):
        """Rules 4 and 5. A reopened task is open again, so it needs a free slot."""
        if (self.status, new_status) not in ALLOWED:
            raise RuleViolation(f"cannot move from {self.status} to {new_status}")
        if self.status == "done" and self.assignee_id is not None and assignee_open_count >= MAX_OPEN:
            raise RuleViolation(f"assignee already has {MAX_OPEN} open tasks")
        self.status = new_status
        self.completed_at = now if new_status == "done" else None
```

Six rules, one file, no imports except `errors`. A product owner can read this file and check it against section 2.1.

### 8.4 The service shrinks to a director

```python
# taskboard/services.py
from datetime import datetime, timezone

from . import mailer
from .domain import Task
from .errors import NotFound


def _now():
    return datetime.now(timezone.utc).isoformat()


def _open_count_of(uow, user_id):
    return 0 if user_id is None else uow.tasks.open_count(user_id)


def create_task(uow, project_id, title, assignee_id=None):
    task = Task.new(project_id, title, _now())             # validates the title
    with uow:
        if not uow.projects.exists(project_id):
            raise NotFound("project not found")
        if assignee_id is not None:
            task.assign(assignee_id,
                        is_member=uow.projects.is_member(project_id, assignee_id),
                        open_count=uow.tasks.open_count(assignee_id))
        uow.tasks.add(task)
        uow.tasks.add_audit(task.id, "created", task.created_at)
        if assignee_id is not None:
            mailer.send_email(uow.users.email_of(assignee_id), f"New task: {task.title}")
        uow.commit()
        return task


def update_task(uow, task_id, assignee_id=None, status=None):
    with uow:
        task = uow.tasks.get(task_id)
        if task is None:
            raise NotFound("task not found")
        stamp = _now()
        if assignee_id is not None:
            task.assign(assignee_id,
                        is_member=uow.projects.is_member(task.project_id, assignee_id),
                        open_count=uow.tasks.open_count(assignee_id))
            uow.tasks.add_audit(task.id, "assigned", stamp)
            mailer.send_email(uow.users.email_of(assignee_id), f"Task assigned: {task.title}")
        if status is not None:
            task.change_status(status, stamp,
                               assignee_open_count=_open_count_of(uow, task.assignee_id))
            uow.tasks.add_audit(task.id, f"status:{status}", stamp)
        uow.tasks.save(task)
        uow.commit()
        return task


def get_task(uow, task_id):
    with uow:
        task = uow.tasks.get(task_id)
        if task is None:
            raise NotFound("task not found")
        return task


def list_tasks(uow, project_id, status=None):
    with uow:
        return uow.tasks.list(project_id, status)
```

No `if (task.status, status) not in ALLOWED` any more: the service does not know what the allowed moves are. It only asks.

### 8.5 Rules tested with no set-up at all

The best test is one that needs nothing. These domain tests build a `Task` directly and call a method. No fake, no unit of work, no fixture file:

```python
# tests/test_domain.py
import pytest

from taskboard.domain import ALLOWED, MAX_OPEN, Task
from taskboard.errors import InvalidInput, RuleViolation


def task(status="todo", assignee=None):
    return Task(1, 1, "t", status, assignee, "2026-01-01T00:00:00")


def test_new_trims_and_validates_the_title():
    assert Task.new(1, "  hello ", "now").title == "hello"
    for bad in ("", "   ", "x" * 121):
        with pytest.raises(InvalidInput):
            Task.new(1, bad, "now")


def test_assign_needs_membership():
    with pytest.raises(RuleViolation, match="not a member"):
        task().assign(3, is_member=False, open_count=0)


def test_assign_refuses_when_the_person_is_full():
    with pytest.raises(RuleViolation, match="3 open tasks"):
        task().assign(1, is_member=True, open_count=MAX_OPEN)
    t = task()
    t.assign(1, is_member=True, open_count=MAX_OPEN - 1)
    assert t.assignee_id == 1


def test_assigning_a_done_task_is_free():
    t = task(status="done")
    t.assign(1, is_member=True, open_count=MAX_OPEN)         # a done task adds no load
    assert t.assignee_id == 1


def test_assigning_to_the_same_person_is_free():
    t = task(assignee=1)
    t.assign(1, is_member=True, open_count=MAX_OPEN)          # they already carry this task
    assert t.assignee_id == 1


@pytest.mark.parametrize("old", ["todo", "doing", "done"])
@pytest.mark.parametrize("new", ["todo", "doing", "done"])
def test_every_status_move(old, new):
    t = task(status=old)
    if (old, new) in ALLOWED:
        t.change_status(new, "now")
        assert t.status == new
    else:
        with pytest.raises(RuleViolation, match="cannot move"):
            t.change_status(new, "now")
        assert t.status == old, "a refused move must not change the task"


def test_done_records_completion_and_reopen_clears_it():
    t = task(status="doing")
    t.change_status("done", "2026-02-02T00:00:00")
    assert t.completed_at == "2026-02-02T00:00:00"
    t.change_status("todo", "later")
    assert t.completed_at is None


def test_reopening_needs_a_free_slot():
    t = task(status="done", assignee=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        t.change_status("todo", "now", assignee_open_count=MAX_OPEN)
    assert t.status == "done"
    t.change_status("todo", "now", assignee_open_count=MAX_OPEN - 1)
    assert t.status == "todo"
```

```bash run
python -m pytest -q -p no:cacheprovider tests/test_domain.py
```
```text
................                                                         [100%]
16 passed in 0.08s
```

Sixteen test results (the parametrized test covers all nine status moves) check **every** rule. Run the whole suite to prove nothing outside moved:

```bash run
python -m pytest -q -p no:cacheprovider tests
```
```text
....................................................                     [100%]
52 passed in 0.34s
```

### 8.6 What a domain model is not

- **It is not the ORM model.** In Django, `models.Model` mixes data, storage and (if you let it) rules. A domain object is a plain class. Whether you separate them is a judgement call (Django developers often put rules on the model methods and accept the coupling, which is a reasonable choice for Django apps).
- **It is not required for every field.** A task's `title` has no rule beyond length; making `title` a clever object would only add noise.
- **It is not a goal.** Add behaviour to an object when you find rules about its *state* scattered around. Rules about *several* objects (transfer money between two accounts) may need a service-level function or a separate domain function.

A common beginner trap is the **anemic domain model**: classes with only fields, and all behaviour in "manager" or "service" classes. That is not wrong everywhere (our `Task` was anemic for two sections and the code was fine), but when the rules grow, moving them next to the data pays off, as the test file above shows.

### Try it: add a rule to the domain

Add rule 8: "a task cannot be moved to `doing` unless it has an assignee." Where do you edit? Which existing tests break?

<details><summary>Answer</summary>

One check in `Task.change_status`: `if new_status == "doing" and self.assignee_id is None: raise RuleViolation("assign someone first")`. Add a test to `test_domain.py`. Existing tests that move an **unassigned** task to `doing` break: in the API safety net `test_status_flow` and `test_list_filters_by_status` (they never assign). That is correct and expected: the rule changed the behaviour, so those tests must assign someone first. Notice that you edited **one** rule file and a few test set-ups; the service and the route did not change.

</details>

## 9. Events and the outbox

### 9.1 The pain, proved

So far, assigning a task sends an e-mail from **inside** the service, before `commit()`. There are two failure modes. Run them and see.

**Failure 1: the e-mail is sent for a change that is rolled back.** We ask for an assignment *and* an illegal status move in one request. The status move fails, so the whole request is rolled back, but the e-mail already left:

```bash run
python - <<'EOF'
import sys
sys.path.insert(0, "tests")
from fake_uow import fresh
from taskboard import mailer, services
from taskboard.errors import RuleViolation

store, uow = fresh()
task = services.create_task(uow(), 1, "Write docs")
try:
    services.update_task(uow(), task.id, assignee_id=2, status="done")     # todo -> done is illegal
except RuleViolation as e:
    print("request failed       :", e)
print("assignee afterwards  :", services.get_task(uow(), task.id).assignee_id)
print("e-mails that were sent:", mailer.SENT)
EOF
```
```text
request failed       : cannot move from todo to done
assignee afterwards  : None
e-mails that were sent: [('ben@example.com', 'Task assigned: Write docs')]
```

Ben received "Task assigned: Write docs" for a task that **was never assigned to him**.

**Failure 2: the other order.** Send the e-mail *after* the commit, and a failing provider breaks the request that has already saved its data. The client sees an error, retries, and creates the task twice:

```bash run
python - <<'EOF'
import sys
sys.path.insert(0, "tests")
from fake_uow import fresh
from taskboard import mailer, services

store, uow = fresh()
for attempt in (1, 2):
    try:
        task = services.create_task(uow(), 1, "Call the client")              # committed
        mailer.send_email("bounce@example.com", f"New task: {task.title}")     # sent after commit: fails
    except mailer.MailError as e:
        print(f"attempt {attempt}: client sees an error ({e})")
with uow() as check:
    print("tasks in the database:", [t.title for t in check.tasks.list(1)])
EOF
```
```text
attempt 1: client sees an error (provider rejected bounce@example.com)
attempt 2: client sees an error (provider rejected bounce@example.com)
tasks in the database: ['Call the client', 'Call the client']
```

Two identical tasks, and still no e-mail. Neither order is right. This is the pain from the log (P5), and it is a famous one: **you cannot make a database commit and an e-mail send atomic**, because they are two different systems. The question is what to do instead.

### 9.2 The idea: save the *intention*, deliver it later

Do not send the e-mail in the request. Instead, in the **same transaction** that saves the task, also save a row that says "someone should be told that this task was assigned". That row is an **event** in an **outbox** table. Because it is in the same transaction, it is saved if and only if the task change is saved. A separate step, the **dispatcher**, reads pending rows and performs the real work (sending the mail), then marks them done.

```text
   request                         later (a few ms, or after a restart)
   -------                         ------------------------------------
   BEGIN                           read pending outbox rows
     save task                     for each: send the e-mail
     save outbox row  <-- same     mark the row sent  (own transaction)
   COMMIT                          if sending fails: row stays pending -> try again
```

Guarantees, stated precisely:

| Event | Result |
|---|---|
| Request fails and rolls back | No outbox row, so no e-mail. (Failure 1 fixed.) |
| Request commits, provider is down | Row stays pending; the dispatcher retries later. The client got a success. (Failure 2 fixed.) |
| Process dies after commit | The row is in the database; a restarted dispatcher sends it. Nothing lost. |
| Process dies after sending but before marking sent | The e-mail is sent **again** on the next run. This is **at-least-once** delivery. |

The last row is the price. Cure it as in swe.08: make the consumer **idempotent**. We send each e-mail with a key derived from the outbox row (`outbox-17`), and the mailer ignores a key it has already seen. A real provider would store that key (many accept an idempotency or message-ID header).

### 9.3 Domain events

A **domain event** is a small immutable record of something that happened, named in the past tense: `TaskAssigned`, `TaskStatusChanged`. The task *records* its events as it changes, and the service *publishes* them (writes them to the outbox) before committing. The task still knows nothing about e-mail or databases:

```diff
# taskboard/domain.py
- from dataclasses import dataclass
-
- from .errors import InvalidInput, RuleViolation
+ from dataclasses import asdict, dataclass, field, replace
+
+ from .errors import InvalidInput, RuleViolation
```

```diff
# taskboard/domain.py
- @dataclass
- class Task:
+ @dataclass(frozen=True)
+ class TaskAssigned:
+     assignee_id: int
+     title: str
+     is_new: bool                  # True when the task was assigned at creation
+
+
+ @dataclass(frozen=True)
+ class TaskStatusChanged:
+     status: str
+
+
+ @dataclass
+ class Task:
```

```diff
# taskboard/domain.py
-     completed_at: str | None = None
-
+     completed_at: str | None = None
+     events: list = field(default_factory=list, repr=False, compare=False)
+
+     def __copy__(self):
+         return replace(self, events=[])        # a copy must never share pending events
```

```diff
# taskboard/domain.py
-         self.assignee_id = user_id
+         self.assignee_id = user_id
+         self.events.append(TaskAssigned(user_id, self.title, is_new=self.id is None))
```

```diff
# taskboard/domain.py
-         self.completed_at = now if new_status == "done" else None
+         self.completed_at = now if new_status == "done" else None
+         self.events.append(TaskStatusChanged(new_status))
+
+
+ def drain_events(task):
+     """Take the task's pending events out, as (kind, payload) pairs ready to store."""
+     pending, task.events = task.events, []
+     return [(type(e).__name__, {"task_id": task.id, **asdict(e)}) for e in pending]
```

The `is_new` flag lets the mail handler keep the old subject lines ("New task" versus "Task assigned"), so the outside behaviour does not change.

### 9.4 The outbox table, repository and unit of work

```diff
# taskboard/schema.py
-     id INTEGER PRIMARY KEY, task_id INTEGER, action TEXT NOT NULL, at TEXT NOT NULL);
+     id INTEGER PRIMARY KEY, task_id INTEGER, action TEXT NOT NULL, at TEXT NOT NULL);
+ CREATE TABLE IF NOT EXISTS outbox (
+     id INTEGER PRIMARY KEY, kind TEXT NOT NULL, payload TEXT NOT NULL,
+     created_at TEXT NOT NULL, sent_at TEXT);
```

```diff
# taskboard/repo.py
- from .domain import Task
+ import json
+ from dataclasses import dataclass
+
+ from .domain import Task
```

```diff
# taskboard/repo.py
- class SqliteRepos:
-     """The bundle that services receive."""
-     def __init__(self, conn):
-         self.tasks = SqliteTaskRepo(conn)
-         self.projects = SqliteProjectRepo(conn)
-         self.users = SqliteUserRepo(conn)
+ @dataclass
+ class OutboxItem:
+     id: int
+     kind: str
+     payload: dict
+
+
+ class SqliteOutboxRepo:
+     def __init__(self, conn):
+         self.conn = conn
+
+     def add(self, kind, payload, at):
+         self.conn.execute("INSERT INTO outbox (kind, payload, created_at) VALUES (?, ?, ?)",
+                           (kind, json.dumps(payload), at))
+
+     def pending(self, limit=50):
+         rows = self.conn.execute(
+             "SELECT id, kind, payload FROM outbox WHERE sent_at IS NULL ORDER BY id LIMIT ?",
+             (limit,)).fetchall()
+         return [OutboxItem(r["id"], r["kind"], json.loads(r["payload"])) for r in rows]
+
+     def mark_sent(self, item_id, at):
+         self.conn.execute("UPDATE outbox SET sent_at = ? WHERE id = ?", (at, item_id))
+
+
+ class SqliteRepos:
+     """The bundle that services receive."""
+     def __init__(self, conn):
+         self.tasks = SqliteTaskRepo(conn)
+         self.projects = SqliteProjectRepo(conn)
+         self.users = SqliteUserRepo(conn)
+         self.outbox = SqliteOutboxRepo(conn)
```

```diff
# taskboard/uow.py
-         self.tasks, self.projects, self.users = repos.tasks, repos.projects, repos.users
+         self.tasks, self.projects = repos.tasks, repos.projects
+         self.users, self.outbox = repos.users, repos.outbox
```

The services lose the `mailer` import and the two `send_email` calls; instead they publish what the task recorded, **before** `commit()`:

```diff
# taskboard/services.py
- from . import mailer
- from .domain import Task
- from .errors import NotFound
+ from .domain import Task, drain_events
+ from .errors import NotFound
```

```diff
# taskboard/services.py
- def _open_count_of(uow, user_id):
+ def _publish(uow, task):
+     """Write the task's pending events to the outbox, inside the current transaction."""
+     for kind, payload in drain_events(task):
+         uow.outbox.add(kind, payload, _now())
+
+
+ def _open_count_of(uow, user_id):
```

```diff
# taskboard/services.py
-         uow.tasks.add_audit(task.id, "created", task.created_at)
-         if assignee_id is not None:
-             mailer.send_email(uow.users.email_of(assignee_id), f"New task: {task.title}")
-         uow.commit()
+         uow.tasks.add_audit(task.id, "created", task.created_at)
+         _publish(uow, task)
+         uow.commit()
```

```diff
# taskboard/services.py
-             uow.tasks.add_audit(task.id, "assigned", stamp)
-             mailer.send_email(uow.users.email_of(assignee_id), f"Task assigned: {task.title}")
+             uow.tasks.add_audit(task.id, "assigned", stamp)
```

```diff
# taskboard/services.py
-         uow.tasks.save(task)
-         uow.commit()
+         uow.tasks.save(task)
+         _publish(uow, task)
+         uow.commit()
```

### 9.5 The dispatcher and the handlers

The mailer gains the idempotency key we promised, and a `reset()` for tests:

```python
# taskboard/mailer.py
SENT = []          # (to, subject) pairs; a real mailer would talk to SMTP or a provider
_KEYS = set()      # idempotency keys already used


class MailError(Exception):
    pass


def send_email(to, subject, key=None):
    if to.startswith("bounce"):
        raise MailError(f"provider rejected {to}")
    if key is not None:
        if key in _KEYS:
            return                     # already delivered: the provider ignores the repeat
        _KEYS.add(key)
    SENT.append((to, subject))


def reset():
    SENT.clear()
    _KEYS.clear()
```

A handler is a function that reacts to one kind of event. It receives a unit of work (to read what it needs) and the outbox item:

```python
# taskboard/notifications.py
from . import mailer


def on_task_assigned(uow, item):
    p = item.payload
    subject = ("New task: " if p["is_new"] else "Task assigned: ") + p["title"]
    mailer.send_email(uow.users.email_of(p["assignee_id"]), subject, key=f"outbox-{item.id}")


def ignore(uow, item):
    """Events nobody reacts to yet. Listing them keeps 'ignored' different from 'forgotten'."""


HANDLERS = {"TaskAssigned": on_task_assigned, "TaskStatusChanged": ignore}
```

And the dispatcher itself. Every item is delivered in its own transaction, so one bad item cannot block the others:

```python
# taskboard/dispatch.py
import logging
from datetime import datetime, timezone

log = logging.getLogger("taskboard.dispatch")


def dispatch_pending(new_uow, handlers, limit=50):
    """Deliver pending outbox items. Returns (delivered, failed)."""
    with new_uow() as uow:
        items = uow.outbox.pending(limit)
    delivered = failed = 0
    for item in items:
        try:
            with new_uow() as uow:
                handler = handlers.get(item.kind)
                if handler is None:
                    log.warning("no handler for %s (item %s); marking it done", item.kind, item.id)
                else:
                    handler(uow, item)
                uow.outbox.mark_sent(item.id, datetime.now(timezone.utc).isoformat())
                uow.commit()
            delivered += 1
        except Exception:
            log.exception("delivery of outbox item %s failed; it stays pending", item.id)
            failed += 1
    return delivered, failed
```

Finally the routes trigger a delivery run **after the response is sent**, using FastAPI's background tasks (swe.05, section 14). A periodic sweep (a loop in a worker process or a cron job, as in swe.08) would pick up anything the quick path missed:

```diff
# taskboard/main.py
- from fastapi import FastAPI
+ from fastapi import BackgroundTasks, FastAPI
```

```diff
# taskboard/main.py
- from . import services
- from .errors import DomainError, NotFound, InvalidInput, RuleViolation
- from .uow import SqliteUnitOfWork
+ from . import services
+ from .dispatch import dispatch_pending
+ from .errors import DomainError, NotFound, InvalidInput, RuleViolation
+ from .notifications import HANDLERS
+ from .uow import SqliteUnitOfWork
```

```diff
# taskboard/main.py
- def run(use_case, *args):
-     """Run one use case with a fresh unit of work (its own connection and transaction)."""
-     return use_case(SqliteUnitOfWork(os.environ.get("TASKBOARD_DB", "taskboard.db")), *args)
+ def new_uow():
+     return SqliteUnitOfWork(os.environ.get("TASKBOARD_DB", "taskboard.db"))
+
+
+ def run(use_case, *args):
+     """Run one use case with a fresh unit of work (its own connection and transaction)."""
+     return use_case(new_uow(), *args)
+
+
+ def deliver():
+     dispatch_pending(new_uow, HANDLERS)
```

```diff
# taskboard/main.py
- def create_task(project_id: int, body: NewTask):
-     return task_json(run(services.create_task, project_id, body.title, body.assignee_id))
-
-
- @app.patch("/tasks/{task_id}")
- def update_task(task_id: int, body: TaskPatch):
-     return task_json(run(services.update_task, task_id, body.assignee_id, body.status))
+ def create_task(project_id: int, body: NewTask, background: BackgroundTasks):
+     task = run(services.create_task, project_id, body.title, body.assignee_id)
+     background.add_task(deliver)
+     return task_json(task)
+
+
+ @app.patch("/tasks/{task_id}")
+ def update_task(task_id: int, body: TaskPatch, background: BackgroundTasks):
+     task = run(services.update_task, task_id, body.assignee_id, body.status)
+     background.add_task(deliver)
+     return task_json(task)
```

The fakes need an outbox too (one list in the shared data, copied together with everything else when a transaction starts):

```diff
# tests/fakes.py
-         "tasks": {}, "audit": [], "next_id": 1,
+         "tasks": {}, "audit": [], "outbox": [], "next_id": 1,
```

```diff
# tests/fakes.py
- class FakeRepos:
-     def __init__(self, data):
-         self.tasks = FakeTaskRepo(data)
-         self.projects = FakeProjectRepo(data)
-         self.users = FakeUserRepo(data)
+ class FakeOutboxRepo:
+     def __init__(self, data):
+         self.data = data
+
+     def add(self, kind, payload, at):
+         rows = self.data["outbox"]
+         rows.append({"id": len(rows) + 1, "kind": kind, "payload": copy.deepcopy(payload),
+                      "sent_at": None})
+
+     def pending(self, limit=50):
+         rows = [r for r in self.data["outbox"] if r["sent_at"] is None][:limit]
+         return [OutboxItem(r["id"], r["kind"], copy.deepcopy(r["payload"])) for r in rows]
+
+     def mark_sent(self, item_id, at):
+         for r in self.data["outbox"]:
+             if r["id"] == item_id:
+                 r["sent_at"] = at
+
+
+ class FakeRepos:
+     def __init__(self, data):
+         self.tasks = FakeTaskRepo(data)
+         self.projects = FakeProjectRepo(data)
+         self.users = FakeUserRepo(data)
+         self.outbox = FakeOutboxRepo(data)
```

```diff
# tests/fakes.py
- from taskboard.repo import SqliteRepos
+ from taskboard.repo import OutboxItem, SqliteRepos
```

```diff
# tests/fake_uow.py
- from fakes import FakeProjectRepo, FakeTaskRepo, FakeUserRepo, world_data
+ from fakes import FakeOutboxRepo, FakeProjectRepo, FakeTaskRepo, FakeUserRepo, world_data
```

```diff
# tests/fake_uow.py
-         self.users = FakeUserRepo(self.work)
-         return self
+         self.users = FakeUserRepo(self.work)
+         self.outbox = FakeOutboxRepo(self.work)
+         return self
```

Three older tests mention the mailer. `conftest.py` and the unit-test fixture switch to `mailer.reset()`, and the unit tests no longer need a mailer fixture at all, because the services do not touch it any more:

```diff
# tests/conftest.py
-     mailer.SENT.clear()
+     mailer.reset()
```

```diff
# tests/test_services_unit.py
- from taskboard import mailer, services
+ from taskboard import services
```

```diff
# tests/test_services_unit.py
- @pytest.fixture(autouse=True)
- def quiet_mailer():
-     mailer.SENT.clear()      # services still call the global mailer (we fix that in section 9)
-
-
- @pytest.fixture
- def world():
+ @pytest.fixture
+ def world():
```

One of the "pain" tests described the **old** behaviour: a failing provider fails the request (HTTP 500) and nothing is saved. With the outbox this is deliberately different and better: the request succeeds because the task *is* saved, and the e-mail stays pending. We change the test on purpose, and say so, instead of hiding the change:

```diff
# tests/test_pain.py
- def test_failed_email_leaves_no_half_saved_task(client):
-     r = make(client, title="for bounce", assignee=4)   # the mail provider rejects this address
-     assert r.status_code == 500
-     make(client, title="next")                         # an unrelated, perfectly valid request
-     titles = [t["title"] for t in client.get("/projects/1/tasks").json()]
-     assert titles == ["next"], f"the failed request left traces behind: {titles}"
+ def test_a_failing_mail_provider_neither_loses_nor_corrupts_data(client):
+     # DELIBERATE behaviour change (section 9): the task is saved, the request succeeds,
+     # the e-mail stays pending in the outbox. Before: HTTP 500 and a half-saved shared transaction.
+     r = make(client, title="for bounce", assignee=4)   # the mail provider rejects this address
+     assert r.status_code == 201
+     make(client, title="next")
+     titles = [t["title"] for t in client.get("/projects/1/tasks").json()]
+     assert titles == ["for bounce", "next"], titles
```

### 9.6 Tests for events, the outbox and delivery

```python
# tests/test_outbox.py
import copy

import pytest

from fake_uow import fresh
from fakes import fake_world, sqlite_world
from taskboard import mailer, services
from taskboard.dispatch import dispatch_pending
from taskboard.domain import Task
from taskboard.errors import RuleViolation
from taskboard.notifications import HANDLERS, on_task_assigned


# ---- the outbox repository, same contract for both implementations -----------------------
@pytest.fixture(params=["fake", "sqlite"])
def repos(request):
    return fake_world() if request.param == "fake" else sqlite_world()


def test_outbox_roundtrip_in_order(repos):
    repos.outbox.add("A", {"n": 1}, "t")
    repos.outbox.add("B", {"n": 2}, "t")
    items = repos.outbox.pending()
    assert [(i.kind, i.payload) for i in items] == [("A", {"n": 1}), ("B", {"n": 2})]
    repos.outbox.mark_sent(items[0].id, "t")
    assert [i.kind for i in repos.outbox.pending()] == ["B"], "sent items leave the pending list"
    assert len(repos.outbox.pending(limit=0)) == 0, "limit must be respected"


# ---- events recorded by the domain ----------------------------------------------------------
def test_assign_records_an_event_and_a_copy_does_not_share_it():
    t = Task(5, 1, "x", "todo", None, "now")
    t.assign(1, is_member=True, open_count=0)
    assert len(t.events) == 1
    assert copy.copy(t).events == [], "a stored copy must not carry pending events"


# ---- publishing happens in the same transaction -----------------------------------------------
@pytest.fixture
def world():
    mailer.reset()
    return fresh()


def pending_kinds(uow):
    with uow() as u:
        return [i.kind for i in u.outbox.pending()]


def test_assigning_publishes_an_event(world):
    store, uow = world
    t = services.create_task(uow(), 1, "x", assignee_id=1)
    with uow() as u:
        items = u.outbox.pending()
    assert [i.kind for i in items] == ["TaskAssigned"]
    assert items[0].payload == {"task_id": t.id, "assignee_id": 1, "title": "x", "is_new": True}
    assert mailer.SENT == [], "the request itself sends nothing"


def test_a_rolled_back_change_publishes_nothing(world):
    store, uow = world
    t = services.create_task(uow(), 1, "x")
    with pytest.raises(RuleViolation):
        services.update_task(uow(), t.id, assignee_id=2, status="done")
    assert pending_kinds(uow) == [], "no outbox row for a change that never happened"


# ---- delivery ---------------------------------------------------------------------------------
def test_dispatch_delivers_exactly_once(world):
    store, uow = world
    services.create_task(uow(), 1, "Ship it", assignee_id=1)
    assert dispatch_pending(uow, HANDLERS) == (1, 0)
    assert mailer.SENT == [("ana@example.com", "New task: Ship it")]
    assert dispatch_pending(uow, HANDLERS) == (0, 0), "a delivered item must not be delivered again"


def test_a_failed_delivery_stays_pending_and_is_retried(world):
    store, uow = world
    services.create_task(uow(), 1, "x", assignee_id=4)             # bounce@example.com is rejected
    assert dispatch_pending(uow, HANDLERS) == (0, 1)
    assert pending_kinds(uow) == ["TaskAssigned"], "the item must wait, not vanish"
    store.data["users"][4] = "fixed@example.com"                    # the address is corrected
    assert dispatch_pending(uow, HANDLERS) == (1, 0)
    assert mailer.SENT == [("fixed@example.com", "New task: x")]


def test_a_crash_after_sending_does_not_send_twice(world):
    store, uow = world
    services.create_task(uow(), 1, "x", assignee_id=1)

    def send_then_crash(u, item):                  # the process dies before 'mark_sent' is committed
        on_task_assigned(u, item)
        raise RuntimeError("power cut")

    assert dispatch_pending(uow, {"TaskAssigned": send_then_crash}) == (0, 1)
    assert len(mailer.SENT) == 1 and pending_kinds(uow) == ["TaskAssigned"]
    assert dispatch_pending(uow, HANDLERS) == (1, 0)           # restart: delivered again...
    assert len(mailer.SENT) == 1, "...but the idempotency key stops the second e-mail"
```

```bash run
python -m pytest -q -p no:cacheprovider tests
```
```text
............................................................             [100%]
60 passed in 0.37s
```

Look at what the suite proves now: assigning writes an event in the same transaction; a rolled-back change leaves no event; a failing provider keeps the item pending; a crash between "send" and "mark sent" gives **one** e-mail, not two. Three of those four lines were impossible to say with the first version of this program.

Now show the first failure again, with the new code:

```bash run
python - <<'EOF'
import sys
sys.path.insert(0, "tests")
from fake_uow import fresh
from taskboard import mailer, services
from taskboard.dispatch import dispatch_pending
from taskboard.errors import RuleViolation
from taskboard.notifications import HANDLERS

store, uow = fresh()
task = services.create_task(uow(), 1, "Write docs")
try:
    services.update_task(uow(), task.id, assignee_id=2, status="done")
except RuleViolation as e:
    print("request failed       :", e)
print("assignee afterwards  :", services.get_task(uow(), task.id).assignee_id)
print("dispatch result      :", dispatch_pending(uow, HANDLERS))
print("e-mails that were sent:", mailer.SENT)
EOF
```
```text
request failed       : cannot move from todo to done
assignee afterwards  : None
dispatch result      : (0, 0)
e-mails that were sent: []
```

### 9.7 How far to take this

The outbox is the first piece of **event-driven design** in this course, so be clear about its scope.

| Question | Answer in Taskboard |
|---|---|
| Who produces events? | The domain objects, when their state changes. |
| Who consumes them? | Handlers in `notifications.py`, run by the dispatcher. |
| How are they delivered? | From the database, in order, at least once, after the transaction. |
| Is there a message broker? | No. The outbox table is the queue. A broker (RabbitMQ, Kafka, Redis streams) becomes useful when **other services** must consume the events; the outbox then feeds the broker (swe.08, "outbox" in the project). |
| Is the order guaranteed? | Per dispatcher, by outbox `id`. With several dispatchers running in parallel it is not; if order matters, partition by task id. |

Two honest warnings. First, events make a program **harder to follow**: "why did an e-mail go out?" now needs you to search for who handles `TaskAssigned`. Use them where the *reaction* really is separate from the action (mail, search index, webhooks, analytics) and not for ordinary function calls. Second, the audit line is still written directly by the service even though the event contains the same information. That duplication is a conscious shortcut: audit rows must be in the same transaction, and the outbox is too, so you could derive the audit from events later. Do that only when the duplication hurts.

### Try it: what if two dispatchers run at once?

Two worker processes call `dispatch_pending` at the same moment on the same database. Can an item be sent twice? What would you add?

<details><summary>Answer</summary>

Yes. Both read the same `pending` rows before either marks them. The idempotency key protects the **mail** (the second send is ignored), but both do the work. To avoid wasted work or to guarantee single processing, **claim** the row: `UPDATE outbox SET claimed_by = ?, claimed_at = ? WHERE id = ? AND sent_at IS NULL AND claimed_at IS NULL` and process only if one row changed (the atomic claim from the `JobQueue` in swe.08, with a lease that expires so a crashed worker's claim can be taken over). In PostgreSQL you would use `SELECT ... FOR UPDATE SKIP LOCKED`.

</details>

## 10. The finished shape, and when not to build it

### 10.1 The composition root

Everything is wired inside the module-level `main.py`: it picks `SqliteUnitOfWork`, `HANDLERS`, and the e-mail module. In a layered design there should be **one place** that knows all the concrete pieces and glues them together: the **composition root**. Everything else receives its dependencies as arguments. We make `main.py` that place by turning the module into a function, `create_app(new_uow)`:

```python
# taskboard/main.py
import os

from fastapi import BackgroundTasks, FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from . import services
from .dispatch import dispatch_pending
from .errors import DomainError, InvalidInput, NotFound, RuleViolation
from .notifications import HANDLERS
from .uow import SqliteUnitOfWork

STATUS_FOR = {NotFound: 404, InvalidInput: 422, RuleViolation: 409}


class NewTask(BaseModel):
    title: str
    assignee_id: int | None = None


class TaskPatch(BaseModel):
    assignee_id: int | None = None
    status: str | None = None


def task_json(t):
    return {"id": t.id, "project_id": t.project_id, "title": t.title, "status": t.status,
            "assignee_id": t.assignee_id, "completed_at": t.completed_at}


def sqlite_uow():
    return SqliteUnitOfWork(os.environ.get("TASKBOARD_DB", "taskboard.db"))


def create_app(new_uow=sqlite_uow):
    """The composition root: the only place that chooses concrete implementations."""
    app = FastAPI(title="Taskboard")

    @app.exception_handler(DomainError)
    def domain_error_to_http(request, exc):
        return JSONResponse({"detail": str(exc)}, status_code=STATUS_FOR.get(type(exc), 400))

    def deliver():
        dispatch_pending(new_uow, HANDLERS)

    @app.post("/projects/{project_id}/tasks", status_code=201)
    def create_task(project_id: int, body: NewTask, background: BackgroundTasks):
        task = services.create_task(new_uow(), project_id, body.title, body.assignee_id)
        background.add_task(deliver)
        return task_json(task)

    @app.patch("/tasks/{task_id}")
    def update_task(task_id: int, body: TaskPatch, background: BackgroundTasks):
        task = services.update_task(new_uow(), task_id, body.assignee_id, body.status)
        background.add_task(deliver)
        return task_json(task)

    @app.get("/tasks/{task_id}")
    def get_task(task_id: int):
        return task_json(services.get_task(new_uow(), task_id))

    @app.get("/projects/{project_id}/tasks")
    def list_tasks(project_id: int, status: str | None = None):
        return [task_json(t) for t in services.list_tasks(new_uow(), project_id, status)]

    return app


app = create_app()
```

A bonus appears: the whole HTTP layer can now be tested **with the fake unit of work**, with no database at all. That tests status codes, JSON and error mapping, and nothing else:

```python
# tests/test_api_fake.py
from fastapi.testclient import TestClient

from fake_uow import fresh
from taskboard import mailer
from taskboard.main import create_app


def test_http_layer_without_any_database():
    mailer.reset()
    store, uow = fresh()
    client = TestClient(create_app(uow))
    r = client.post("/projects/1/tasks", json={"title": "x", "assignee_id": 1})
    assert r.status_code == 201 and r.json()["assignee_id"] == 1
    assert client.post("/projects/1/tasks", json={"title": " "}).status_code == 422, "InvalidInput -> 422"
    assert client.post("/projects/99/tasks", json={"title": "x"}).status_code == 404, "NotFound -> 404"
    assert client.patch("/tasks/1", json={"status": "done"}).status_code == 409, "RuleViolation -> 409"
    assert mailer.SENT == [("ana@example.com", "New task: x")]
```

### 10.2 The dependency rule

Draw the final structure with arrows meaning "imports":

```text
                      +-----------------+
                      |    main.py      |   composition root + HTTP translation
                      +--------+--------+
                 uses          |          uses
          +--------------------+--------------------+
          v                    v                     v
   +-------------+      +-------------+      +----------------+
   |  services   |      |  dispatch   |      |  uow / repo /  |  infrastructure:
   | (use cases) |      | notifications|     |  db / mailer   |  SQLite, e-mail
   +------+------+      +------+------+      +--------+-------+
          | uses               |                      |
          v                    v                      v
   +-----------------------------------------------------------+
   |   domain.py  (Task, events, rules)      errors.py         |   imports nothing else
   +-----------------------------------------------------------+
```

The **dependency rule**: arrows point *inwards* towards the domain. The domain knows nothing about services, SQL, HTTP or e-mail. Services know the domain and talk to storage only through the unit of work they are given. This is why the fakes work: the service never knew which implementation it had.

A rule that is not enforced decays. Teams write it down and then break it on a busy Friday. Because Python has `ast`, you can make the rule a **test**:

```python
# tests/test_architecture.py
import ast
from pathlib import Path

PKG = Path(__file__).resolve().parent.parent / "taskboard"

# For each inner file: the only modules it may import. ('.x' means taskboard/x.py)
ALLOWED = {
    "domain.py": {"dataclasses", ".errors"},
    "services.py": {"datetime", ".domain", ".errors"},
    "notifications.py": {".mailer"},
    "dispatch.py": {"logging", "datetime"},
}


def imports(path):
    found = set()
    for node in ast.walk(ast.parse(Path(path).read_text())):
        if isinstance(node, ast.Import):
            found.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.module:
                found.add("." + node.module.split(".")[0])
            elif node.level:
                found.update("." + a.name for a in node.names)
            else:
                found.add(node.module.split(".")[0])
    return found


def forbidden(path, allowed):
    return sorted(imports(path) - allowed)


def test_inner_layers_import_only_what_the_dependency_rule_allows():
    for name, allowed in ALLOWED.items():
        extra = forbidden(PKG / name, allowed)
        assert not extra, (f"{name} imports {extra}. Inner layers must not depend on outer ones: "
                           f"pass the dependency in as an argument instead")
```

```bash run
python -m pytest -q -p no:cacheprovider tests/test_architecture.py
```
```text
.                                                                        [100%]
1 passed in 0.07s
```

Now watch it catch a violation. A "quick fix" on a busy day imports `sqlite3` into the services:

```bash run
python - <<'EOF'
import sys, tempfile, pathlib
sys.path.insert(0, "tests")
from test_architecture import ALLOWED, forbidden

src = pathlib.Path("taskboard/services.py").read_text()
bad = pathlib.Path(tempfile.mkdtemp()) / "services.py"
bad.write_text("import sqlite3\nfrom .repo import SqliteTaskRepo\n" + src)
print("violations:", forbidden(bad, ALLOWED["services.py"]))
EOF
```
```text
violations: ['.repo', 'sqlite3']
```

The test turns a design principle into something that fails in CI, which is the only way principles survive.

### 10.3 The bill

Time to be honest about what the refactoring cost and what it bought. Lines of code per file, counting everything in `taskboard/` and `tests/`:

```bash run
python - <<'EOF'
import pathlib
def loc(p):
    return sum(1 for line in pathlib.Path(p).read_text().splitlines() if line.strip())
print("taskboard/ (the program)")
total = 0
for p in sorted(pathlib.Path("taskboard").glob("*.py")):
    n = loc(p); total += n if p.name != "__init__.py" else 0
    print(f"  {p.name:18}{n:4}")
print(f"  {'total':18}{total:4}   (the first version: 142 lines in 4 files; main.py alone had 95)")
t = sum(loc(p) for p in pathlib.Path("tests").glob("*.py"))
print(f"tests/ total        {t:4}   (the first version had 8 + 3 = 11 tests)")
EOF
```
```text
taskboard/ (the program)
  __init__.py          0
  db.py                8
  dispatch.py         23
  domain.py           55
  errors.py            8
  mailer.py           15
  main.py             47
  notifications.py     8
  repo.py             79
  schema.py           23
  services.py         53
  uow.py              16
  total              335   (the first version: 142 lines in 4 files; main.py alone had 95)
tests/ total         486   (the first version had 8 + 3 = 11 tests)
```

```bash run
python -m pytest -q -p no:cacheprovider --collect-only tests | tail -n 3
```
```text
tests/test_services_unit.py::test_without_commit_nothing_is_kept

62 tests collected in 0.11s
```

| | First version | Now |
|---|---|---|
| Program files | 4 | 11 |
| Program lines | about 140 | roughly twice as many |
| Tests | 11, all through HTTP | 62, most of them pure Python |
| Rule 3 enforced in | 1 of 3 places | 1 of 1 (`Task`) |
| A failed request | could corrupt a later one | rolls back, tested |
| E-mail | could be lost, doubled, or sent for rolled-back data | at-least-once with an idempotency key, tested |

The program roughly **doubled** in size. That is the cost. It bought five concrete things, each tied to a pain we measured. If your own project does not have those pains, you should **not** pay this price. Use the table in section 1.4 to stop at the right row.

### 10.4 When not to build it

| Situation | What to do instead |
|---|---|
| A prototype, a script, a weekend project | One file. Come back when it hurts. |
| A CRUD admin with no rules | Use the framework as intended (Django admin, FastAPI + SQLAlchemy, direct queries). |
| Only **reads** (`GET` lists, reports) | Let them query the database directly and return rows. A "read side" that skips the domain model is normal and often wiser. Our `list_tasks` is one line away from that. |
| A small team, one deployment | The first one or two rows of the ladder. Services plus a unit of work often cover 80% of the benefit. |
| You use an ORM that already has sessions | The ORM *is* your unit of work and your repository. Wrap it only if you need fakes or a firewall against ORM details leaking into rules. |

And when you do build it, resist these extras until pain demands them: an interface (`Protocol`) for each repository (Python's duck typing already gives you substitutability; add a `Protocol` when several implementations really exist and a type checker should police them), dependency injection frameworks, a generic `BaseRepository[T]`, a command bus, event sourcing, CQRS with separate databases. All are real tools used in real systems. None of them is a prerequisite for a clean program.

**Further reading** (free or standard references): *Architecture Patterns with Python* by Harry Percival and Bob Gregory (often called "Cosmic Python", free online) is the source of this chapter's repository / unit of work / events progression and goes much further. *Domain-Driven Design* by Eric Evans is the origin of the domain-model vocabulary. *A Philosophy of Software Design* by John Ousterhout argues for deep modules and against needless layers, a useful counterweight.

### Try it: draw the line

Your teammate proposes this change to `services.py`: `from .main import task_json` so that services can return ready-made JSON. Which rule does it break, and what is the correct fix?

<details><summary>Answer</summary>

It makes an inner layer (services) depend on an outer one (`main`, the web layer), reversing the arrow. Soon services need FastAPI to be importable, a CLI cannot reuse them without the web stack, and the architecture test fails. The fix is to return the domain object (`Task`) from the service and let the **web layer** convert it to JSON, which is exactly what `task_json` in `main.py` does today.

</details>


## 11. Monolith, modular monolith or microservices?

### 11.1 Three shapes

| Shape | What it is | Deploy unit | Data |
|---|---|---|---|
| **Monolith** | One program, one deployment. Taskboard is one. | 1 | one database |
| **Modular monolith** | Still one deployment, but inside it the code is divided into modules with clear public interfaces and no reaching into each other's tables. | 1 | one database, but each module owns its tables |
| **Microservices** | Several small programs, each deployed on its own, each with its own database, talking over the network. | many | one database **per service** |

"Monolith" is not an insult. Most successful products started as one and many remain one. The question to ask is never "which is modern?" but "what problem do we have that only separate deployments solve?"

### 11.2 What actually changes when you split

A function call becomes a network call. Everything below follows from that single fact.

| In a monolith | Across services |
|---|---|
| Call takes nanoseconds and cannot fail halfway | Call takes milliseconds, can time out, can succeed with the reply lost |
| One transaction covers a whole use case | No shared transaction: use events, sagas, compensation |
| A refactor is one pull request | An API change needs a version, a migration period and several teams |
| One log, one debugger, one stack trace | Distributed tracing, correlation ids (swe.09, section 8) |
| `join` across any two tables | Each service owns its data; joins become API calls or copies |
| One deploy, one rollback | N pipelines, N versions that must work together |

Measure the first row yourself. This script compares a plain Python call with an HTTP call to a server **on the same machine** (loopback, the best case: no real network at all):

```python run
import http.client, http.server, json, threading, time


class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"          # keep the connection open between requests
    disable_nagle_algorithm = True         # send the small reply at once (no 40 ms delay)

    def do_GET(self):
        body = json.dumps({"open_count": 2}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
threading.Thread(target=server.serve_forever, daemon=True).start()


def open_count(user_id):                   # the same question, asked in-process
    return {"open_count": 2}


n = 3000
start = time.perf_counter()
for _ in range(n):
    open_count(1)
local = (time.perf_counter() - start) / n

conn = http.client.HTTPConnection("127.0.0.1", server.server_address[1])
start = time.perf_counter()
for _ in range(n):
    conn.request("GET", "/users/1/open")
    json.loads(conn.getresponse().read())
remote = (time.perf_counter() - start) / n

print(f"in-process call      : {local * 1e6:9.2f} microseconds")
print(f"HTTP on this machine : {remote * 1e6:9.2f} microseconds  ({remote / local:,.0f} times slower)")
print("a real network adds roughly 0.5 ms inside one data centre, 20 to 150 ms between continents")
```
```text
in-process call      :      0.09 microseconds
HTTP on this machine :    234.89 microseconds  (2,705 times slower)
a real network adds roughly 0.5 ms inside one data centre, 20 to 150 ms between continents
```

The ratio is the lesson. And the slow part is not the worst part: the worst part is that the second call **can fail in ways the first never can**.

### 11.3 The availability tax

Every dependency in a request path is a chance to fail. If each of N services in a chain is up 99.9% of the time and a request needs all of them, the request succeeds only `0.999^N` of the time:

```python run
for n in (1, 3, 5, 10, 20):
    up = 0.999 ** n
    minutes = (1 - up) * 30 * 24 * 60
    print(f"{n:2} services in the request path -> {up * 100:6.2f}% available, about {minutes:6.0f} min down per month")
```
```text
 1 services in the request path ->  99.90% available, about     43 min down per month
 3 services in the request path ->  99.70% available, about    129 min down per month
 5 services in the request path ->  99.50% available, about    216 min down per month
10 services in the request path ->  99.00% available, about    430 min down per month
20 services in the request path ->  98.02% available, about    856 min down per month
```

Twenty "three nines" services in one request give you roughly 98%, about 14 hours of downtime a month, from services that were each "nearly perfect". Microservices do not remove this arithmetic; good design (caches, async events, fallbacks, keeping the critical path short) only reduces how many services a single request depends on.

### 11.4 Reasons to split, and reasons not to

Good reasons, all of them about **people or load**, not taste:

| Reason | Example |
|---|---|
| **Independent deployment** by independent teams | Payments team ships daily; the reporting team ships monthly and must not block them |
| **Very different scaling** | Image resizing needs 40 CPU-heavy machines; the rest of the app runs on 2 |
| **Different failure tolerance** | The recommendation widget may fail; checkout must not |
| **Different technology needs** | A machine-learning model in Python next to a Go gateway |
| **Security or compliance boundary** | Card data isolated in a small audited service |

Poor reasons: "everyone does it", "the monolith is messy" (a messy monolith becomes a messy *network*), "it will scale" (a single PostgreSQL server and 5 app servers handle surprisingly large products), "resume".

**Conway's law**: a system's structure copies the communication structure of the organisation that builds it. Three developers do not need nine services. A rule of thumb many teams use: a service per team, and a team is more than a few people.

The failure to fear is the **distributed monolith**: services that must be deployed together, call each other in long chains, and share one database. It has all the costs of both designs and the benefits of neither.

### 11.5 The practical path: modular monolith first

You can get most of the design benefits of services without paying the network tax by building a **modular monolith**:

1. **Modules** (packages) with a small public interface. Other modules call only that.
2. **Each module owns its tables.** No other module runs SQL against them; it asks through the interface.
3. **Communication across modules by events** where the reaction is separate (as we did with the outbox), and by direct function calls where the answer is needed now.
4. **Boundaries enforced by tests**, like the `ast` test in section 10.2.

Then, *if and when* a real reason to split appears, the seams already exist. Taskboard's seam is the outbox. Here is what a consumer of `TaskAssigned` would receive: this JSON **is** the contract between the two sides.

```bash run
python - <<'EOF'
import os, tempfile
from taskboard.services import create_task
from taskboard.uow import SqliteUnitOfWork
from taskboard.schema import SCHEMA
from tests.seed import SEED
import sqlite3

path = os.path.join(tempfile.mkdtemp(), "seam.db")
c = sqlite3.connect(path); c.executescript(SCHEMA + SEED); c.close()
create_task(SqliteUnitOfWork(path), 1, "Prepare release notes", assignee_id=2)
for row in sqlite3.connect(path).execute("SELECT id, kind, payload FROM outbox"):
    print(row)
EOF
```
```text
(1, 'TaskAssigned', '{"task_id": 1, "assignee_id": 2, "title": "Prepare release notes", "is_new": true}')
```

Splitting a `notifications` service out of Taskboard would then involve four decisions, each with a trade-off:

| Question | Option | Trade-off |
|---|---|---|
| How does the consumer receive events? | outbox table → message broker → consumer | needs a broker; gives delivery to many consumers |
| It needs the user's e-mail address. Where from? | (a) call a users API on every event | simple, but a runtime dependency: if users is down, no mail |
| | (b) put the e-mail in the event payload | fast, but copies data; stale if the address changes |
| | (c) keep a local copy of the users it cares about, updated by events | most independent, most work |
| What if the event format changes? | add optional fields only; never rename or remove without a version | consumers deployed at different times must keep working |
| How is it deployed and monitored? | its own image, pipeline, dashboards, alerts | the operational bill from swe.09, multiplied |

Look at the payload above. A field renamed from `assignee_id` to `user_id` would silently break every consumer you do not control. That is why an event format is an **API** and gets the same care as a public endpoint.

### 11.6 If you do split: the strangler fig

Never rewrite everything at once. The safe migration is the **strangler fig**: put a router (or Nginx rule) in front, build the new service for one slice of behaviour, send a fraction of that traffic to it, compare results, and grow until the old code for that slice is unused and can be deleted. Each step is reversible. The "big rewrite" is the classic way to lose a year.

### Try it: monolith or services?

A team of 4 builds an online course platform: users, courses, video upload and transcoding, payments, e-mail. Daily traffic: 20,000 visits. Video transcoding takes 2 CPU-minutes per upload and spikes on Mondays. What would you do?

<details><summary>Answer</summary>

**A modular monolith, with one exception.** Four people, modest traffic and one database do not justify seven services. But transcoding is the textbook case from the table: very different load (CPU-heavy, spiky), and it can already be asynchronous. So run it as a **separate worker process** that consumes jobs from a queue (swe.08), possibly on its own machines. That is "a service" in the useful sense (independent scaling) without turning the rest of the application into a network. If payments later need a compliance boundary, that is the next candidate for extraction.

</details>

## 12. Talking to other services safely

Whether it is a payment provider, the e-mail provider, or your own second service, a call over the network needs four protections. Without them, **a slow dependency takes your whole application down**, and that is the most common way systems fail in real life.

### 12.1 Timeouts: the most important line of code

If a call has no timeout, a stuck dependency makes your threads wait for ever; the thread pool fills up; your app stops answering everything, even routes that never use that dependency. Always set a timeout, and set it **on purpose**. Know your library's default:

```bash run
python -c "
import httpx
print('httpx default timeout :', httpx.Client().timeout)
"
```
```text
httpx default timeout : Timeout(timeout=5.0)
```

`httpx` uses 5 seconds for each of connect, read, write and pool. The popular `requests` library has **no timeout at all** unless you pass `timeout=`: a classic production bug (the `requests` documentation says so). Rules of thumb:

- Set separate **connect** (short, 1 to 3 s) and **read** timeouts.
- The timeout must be **shorter than the timeout of whoever is waiting for you**. If the browser gives up after 30 s and you wait 60 s on a dependency, you do work nobody will use.
- Pass a **deadline** down a chain: "you have 800 ms left", not "take as long as you like".

### 12.2 Retries, backoff and jitter

Many failures are brief (a restart, a dropped packet). A retry often succeeds, but badly designed retries make outages worse:

- **Only retry what is safe**: reads, and writes that are idempotent (swe.07 section 13, swe.08 section 11). Retrying "charge the card" without an idempotency key charges twice.
- **Back off**: wait longer after each failure (0.1 s, 0.2 s, 0.4 s...), with a cap.
- **Add jitter**: random variation, so a thousand clients that failed together do not retry together. We use *equal jitter*, the formula from swe.08: half the backoff is fixed, half is random.
- **Limit attempts**: 3 or 4, not infinite.
- **Retry at one layer only.** If service A retries 3 times calling B, and B retries 3 times calling C, then one user action can become 3 × 3 = 9 calls to C; with three layers, 27. During an outage this "retry storm" crushes the dependency that is trying to recover.

The code below is a small, testable retry helper. The clock and the randomness are **arguments**, so tests (and this chapter) never really sleep:

```python
# resilience.py
import random
import time


def retry(fn, *, attempts=4, base=0.1, cap=2.0, retry_on=(Exception,),
          sleep=time.sleep, rand=random.random):
    """Call fn(); on failure wait (equal jitter) and try again, up to `attempts` times."""
    for attempt in range(1, attempts + 1):
        try:
            return fn()
        except retry_on:
            if attempt == attempts:
                raise
            backoff = min(cap, base * 2 ** (attempt - 1))
            sleep(backoff / 2 + rand() * backoff / 2)


class CircuitOpen(Exception):
    """Raised without calling the dependency at all."""


class CircuitBreaker:
    """closed -> (too many failures) -> open -> (after reset_after) -> half-open -> closed or open."""

    def __init__(self, failure_threshold=3, reset_after=10.0, clock=time.monotonic):
        self.failure_threshold = failure_threshold
        self.reset_after = reset_after
        self.clock = clock
        self.state = "closed"
        self.failures = 0
        self.opened_at = None

    def call(self, fn):
        if self.state == "open":
            if self.clock() - self.opened_at < self.reset_after:
                raise CircuitOpen("dependency is failing; not calling it")
            self.state = "half-open"                 # let one probe call through
        try:
            result = fn()
        except Exception:
            self._failure()
            raise
        self.failures = 0
        self.state = "closed"
        return result

    def _failure(self):
        self.failures += 1
        if self.state == "half-open" or self.failures >= self.failure_threshold:
            self.state = "open"
            self.opened_at = self.clock()
```

See the delays it would have waited, with a service that fails three times and then works. `rand` is fixed at 0.5 so the output is repeatable:

```python run
from resilience import retry

outcomes = iter([ConnectionError("down"), ConnectionError("down"), ConnectionError("down"), "ok"])
waits = []


def flaky():
    result = next(outcomes)
    if isinstance(result, Exception):
        raise result
    return result


print("result:", retry(flaky, attempts=4, base=0.1, cap=2.0, sleep=waits.append, rand=lambda: 0.5))
print("waits :", [round(w, 3) for w in waits], "seconds")
print("with 3 layers each retrying 3 times, one request can become", 3 ** 3, "calls at the bottom")
```
```text
result: ok
waits : [0.075, 0.15, 0.3] seconds
with 3 layers each retrying 3 times, one request can become 27 calls at the bottom
```

### 12.3 The circuit breaker

Retries help with short failures. When a dependency is **down for a while**, retrying only adds load and makes every caller wait for the timeout. A **circuit breaker** (named after the electrical device) notices repeated failures and **stops calling** for a while; callers fail instantly and can use a fallback. After a pause it lets one probe request through; if that works the circuit closes again.

```text
        success                       3 failures in a row
   +----------------+            +---------------------------+
   v                |            |                           v
 CLOSED  ---------------------------------------->        OPEN   (calls fail instantly)
   ^                                                        |
   | probe succeeds               reset_after seconds pass  |
   |                                                        v
   +------------------ HALF-OPEN <--------------------------+
                       (one probe call)   probe fails -> back to OPEN
```

Here it is on a timeline with a **fake clock** (we move time by hand, so the demo takes no real seconds):

```python run
from resilience import CircuitBreaker, CircuitOpen

now = [0.0]
breaker = CircuitBreaker(failure_threshold=3, reset_after=10.0, clock=lambda: now[0])
dependency_is_up = [False]


def provider():
    if not dependency_is_up[0]:
        raise TimeoutError("provider timed out")
    return "sent"


def attempt(label):
    try:
        outcome = breaker.call(provider)
    except CircuitOpen:
        outcome = "fast fail (circuit open)"
    except TimeoutError:
        outcome = "timeout (slow!)"
    print(f"t={now[0]:4.0f}s  {label:24} -> {outcome:26} state after: {breaker.state}")


for i in range(1, 6):
    attempt(f"call {i}")
    now[0] += 1
now[0] = 20
dependency_is_up[0] = True
attempt("after 10 s, provider back")
attempt("normal call")
```
```text
t=   0s  call 1                   -> timeout (slow!)            state after: closed
t=   1s  call 2                   -> timeout (slow!)            state after: closed
t=   2s  call 3                   -> timeout (slow!)            state after: open
t=   3s  call 4                   -> fast fail (circuit open)   state after: open
t=   4s  call 5                   -> fast fail (circuit open)   state after: open
t=  20s  after 10 s, provider back -> sent                       state after: closed
t=  20s  normal call              -> sent                       state after: closed
```

Calls 1 to 3 each waited for a real timeout. Calls 4 and 5 failed **instantly** without touching the provider, protecting both sides. After the pause, one probe succeeded and traffic resumed.

### 12.4 Fallbacks and graceful degradation

When a dependency is unavailable, decide **in advance** what the user sees:

| Dependency | Failure | Reasonable behaviour |
|---|---|---|
| E-mail provider | down | queue the mail (outbox), say nothing to the user |
| Recommendation service | slow | show a cached or generic list |
| Payment provider | timeout | **do not guess**: mark the payment "pending", reconcile later, never double charge |
| Search | down | fall back to a simple database `LIKE` query, labelled "limited results" |

The art is to keep the **critical path** (log in, place the order) free of non-critical dependencies, and move everything else behind a queue.

### 12.5 Distributed operations: sagas in one paragraph

Without a shared transaction, a use case that touches two services ("reserve stock, then charge the card") can fail in the middle. The standard answer is a **saga**: a sequence of local transactions, each with a **compensating action** that undoes it ("release the stock"). If step 2 fails, run the compensations for the completed steps in reverse. Sagas are eventually consistent: for a short time the system is half-done, and every step must be idempotent. Prefer designs where you do not need one, by keeping data that must change together inside one service.

### 12.6 What to watch

For each outgoing call, track: request rate, error rate, latency percentiles (p50, p95, p99), and circuit state (swe.09 section 10). Alert on "the e-mail provider's error rate is above 5%", which is a *symptom you can act on*.

### Try it: spot the retry storm

Service A calls service B with `retry(attempts=3)`. B calls the database with its own `retry(attempts=3)`. The database is overloaded, and every query takes longer than B's timeout. How many database queries does one request to A cause, and what should change?

<details><summary>Answer</summary>

Up to **9** (3 attempts by A × 3 attempts by B), and each timed-out query probably still runs inside the database, so the overload gets worse, which causes more timeouts. Change: retry in **one** place only (usually the outermost caller, or the layer that knows the operation is idempotent), add a circuit breaker on B's database calls, and add jitter so clients do not retry in step. Overloaded dependencies recover only if callers back off.

</details>

## 13. System design: a method, not a bag of tricks

### 13.1 What "system design" means

In an interview and in real work, a system design question is: *"Here is a product. Sketch how you would build it so that it works for X users, and tell me what could go wrong."* There is no single right answer. What is judged is the **process**: do you clarify the problem, put numbers on it, choose parts for stated reasons, and name the weak spots?

Here is a method that works for both interviews and real design documents. Follow it in order; do not jump to "we need Kafka" in the first minute.

| Step | Question | Output |
|---|---|---|
| 1. **Requirements** | What must it do (functional)? How well (non-functional: latency, availability, consistency, durability, cost)? What is out of scope? | A short list; 3 to 5 key requirements |
| 2. **Estimates** | How many users, requests per second, data per year? | QPS, storage, bandwidth, with a peak factor |
| 3. **API** | What operations do clients call? | 4 to 8 endpoints with inputs and outputs |
| 4. **Data model** | What are the entities, and what do the main queries look like? | A few tables and the indexes the queries need |
| 5. **High-level design** | Which boxes, and how do they talk? | One diagram: clients, load balancer, app servers, database, cache, queue |
| 6. **Deep dive** | The one or two hardest parts: ID generation, feed ranking, hot keys | A decision with alternatives and reasons |
| 7. **Bottlenecks and failures** | What breaks first at 10×? What if a component dies? | A list with a mitigation each |
| 8. **Trade-offs** | What did you give up? What would make you change your mind? | One honest paragraph |

### 13.2 Step 1: requirements, and the non-functional ones people forget

Functional requirements are easy ("create a task"). The non-functional ones drive the design:

| Quality | Question to ask | Typical effect on design |
|---|---|---|
| **Latency** | "How fast must the page feel?" (e.g. p95 under 300 ms) | caching, fewer round trips, CDN |
| **Availability** | "How much downtime can we accept?" (99.9% is 43 minutes a month) | redundancy, health checks, no single point of failure |
| **Consistency** | "Is it a disaster if two users briefly see different data?" | single primary vs replicas, transactions |
| **Durability** | "Can we ever lose a write?" | replication, backups, synchronous commit |
| **Scale** | "How many users, how fast will it grow?" | partitioning, queues |
| **Cost / simplicity** | "How big is the team? How much can we spend?" | fewer moving parts |

Write down what you will **not** support. "No real-time collaboration, no offline mode" saves a month.

### 13.3 Step 2: back-of-the-envelope estimates

You need the order of magnitude, not three decimals. A few facts make this fast:

- One day has about 86,400 seconds, so call it **10^5**. One million requests a day is about **12 requests per second** on average.
- Traffic is not flat: peak is typically **2 to 5 times** the average.
- Assume a read-to-write ratio from the product (a feed is read 100 times for each post written; a bank statement much less).
- Storage = records per day × bytes per record × days kept × a factor for indexes and replicas (2 to 4 is common).

Turn that into a tiny calculator you can reuse:

```python
# estimate.py
def per_second(per_day):
    return per_day / 86_400


def estimate(*, dau, actions_per_user, read_share, peak=3, bytes_per_write=1_000,
             years=3, overhead=3):
    """Rough sizing. `read_share` = fraction of actions that are reads (0.95 = 95%)."""
    actions_per_day = dau * actions_per_user
    reads = actions_per_day * read_share
    writes = actions_per_day - reads
    storage_gb = writes * 365 * years * bytes_per_write * overhead / 1e9
    return {
        "actions per day": actions_per_day,
        "avg read QPS": per_second(reads),
        "peak read QPS": per_second(reads) * peak,
        "avg write QPS": per_second(writes),
        "peak write QPS": per_second(writes) * peak,
        "storage after years (GB)": storage_gb,
    }


def show(title, **kw):
    print(title)
    for key, value in estimate(**kw).items():
        print(f"  {key:26}{value:>16,.1f}")
```

Use it on three products of very different size. The first is Taskboard as a small team SaaS, the others are bigger:

```python run
from estimate import show

show("Taskboard, 20,000 daily users, 40 actions each, 90% reads",
     dau=20_000, actions_per_user=40, read_share=0.90)
show("A social feed, 10 million daily users, 30 actions each, 98% reads",
     dau=10_000_000, actions_per_user=30, read_share=0.98, bytes_per_write=2_000)
```
```text
Taskboard, 20,000 daily users, 40 actions each, 90% reads
  actions per day                  800,000.0
  avg read QPS                           8.3
  peak read QPS                         25.0
  avg write QPS                          0.9
  peak write QPS                         2.8
  storage after years (GB)             262.8
A social feed, 10 million daily users, 30 actions each, 98% reads
  actions per day              300,000,000.0
  avg read QPS                       3,402.8
  peak read QPS                     10,208.3
  avg write QPS                         69.4
  peak write QPS                       208.3
  storage after years (GB)          39,420.0
```

Read the results as decisions:

- Taskboard peaks at a few dozen requests per second, and a few hundred GB over three years (with the generous overhead factor) fits on one ordinary SSD. **One database server and two app servers are plenty.** Anything fancier is waste (and a reason to remember section 1).
- The feed peaks at thousands of reads per second and gathers terabytes of data: now caching, replicas and partitioning are *required*, not decoration.

### 13.4 Numbers worth remembering

Orders of magnitude on ordinary modern hardware (they vary, the ratios are what matter):

| Operation | Rough cost |
|---|---|
| Read from RAM | 100 ns |
| Send 1 KB over a data-centre network | 10 µs |
| SSD random read | 100 µs |
| Round trip within one data centre | 0.5 ms |
| Disk seek on a spinning disk | 5 to 10 ms |
| Round trip between continents | 100 to 150 ms |
| Simple indexed database query | 1 to 10 ms |

A useful single-machine fact: one well-tuned database server on SSDs can handle thousands of simple queries per second and hundreds of write transactions per second; one app server process typically serves from tens to a few hundred requests per second depending on the work. So when your estimate says "50 requests per second", you do not need a cluster.

### 13.5 The diagram

Draw boxes for **things that run** and arrows for **who calls whom**, labelled with what flows. The standard shape for a web product:

```text
  Clients (browser, mobile)
        |
        v
  [CDN]  static files, images          <- optional, cuts load and latency
        |
        v
  [Load balancer]  health checks, TLS
        |
   +----+-----+---------+
   v          v         v
 [App 1]   [App 2]   [App 3]    stateless: any request to any server
   |          |         |
   +----+-----+----+----+
        |          |
        v          v
  [Cache: Redis]  [Primary DB] --replication--> [Replica DB(s)]
                      |
                      +--> [Queue] --> [Workers] --> e-mail, reports, search index
```

Everything to the left of the databases should be **stateless** and replaceable; all state lives in the stores. The next two sections explain why, and how to scale each box.

### Try it: size a small product

A school app has 3,000 daily users who each do about 25 actions, 80% reads. Estimate the average and peak read QPS and decide whether a single server is enough.

<details><summary>Answer</summary>

Actions per day: 3,000 × 25 = 75,000. Reads: 60,000/day, which is 60,000 ÷ 86,400 ≈ 0.7 per second on average, about 2 per second at a 3× peak. Writes ≈ 0.2 per second. This is nothing. A single small server with SQLite or PostgreSQL does it comfortably. The design effort should go into correctness, backups and deployment (swe.09), not scale. (School apps do have a real peak: the first minute of the school day, or exam results. Ask about *bursts*; if 2,000 people open the page in the same minute, that is 30 per second, still small.)

</details>

## 14. Scaling out the application tier

### 14.1 Vertical and horizontal

**Vertical scaling** ("scale up"): a bigger machine. Simple, no code changes, and it goes a long way. It has a ceiling and a single point of failure.

**Horizontal scaling** ("scale out"): more machines behind a load balancer. It needs the application to be **stateless**, and it also gives redundancy: one server dying is an event, not an outage.

Start vertical for the database (it is hard to scale out) and horizontal for the app tier (it is easy if the app is stateless).

### 14.2 Stateless means "no memory between requests on this server"

If a server keeps something in its own memory (a login session, an uploaded file waiting to be processed, a cache that must be consistent), the next request sent to another server will not find it. Watch it happen:

```python run
import itertools


class Server:
    def __init__(self, name, sessions):
        self.name, self.sessions = name, sessions

    def login(self, user):
        self.sessions[f"sid-{user}"] = user
        return f"sid-{user}"

    def whoami(self, sid):
        return self.sessions.get(sid)


def scenario(title, make_sessions):
    shared = make_sessions()
    servers = [Server("app-1", shared if shared is not None else {}),
               Server("app-2", shared if shared is not None else {})]
    balancer = itertools.cycle(servers)                 # round robin
    first, second = next(balancer), next(balancer)
    sid = first.login("ana")
    print(f"{title}: login on {first.name}, next request on {second.name} -> user = {second.whoami(sid)}")


scenario("sessions in each server's memory", lambda: None)
scenario("sessions in a shared store     ", lambda: {})    # stands in for Redis or the database
```
```text
sessions in each server's memory: login on app-1, next request on app-2 -> user = None
sessions in a shared store     : login on app-1, next request on app-2 -> user = ana
```

With per-server memory, Ana is logged out half the time, "randomly". The cure is to move state **out of the app servers**:

| State | Where it should live |
|---|---|
| Sessions / tokens | a shared store (Redis, the database), or a signed token the client holds (JWT, swe.07) |
| Uploaded files | object storage (S3 and its look-alikes), not the server's disk |
| Background work in progress | the queue and the database (swe.08) |
| Caches | Redis for shared; local caches only for data that may be stale per server |
| Scheduled jobs | one scheduler, or a lock, so N servers do not each run the job (swe.08 section 14) |

**Sticky sessions** (the load balancer always sends a user to the same server) are a patch: they hide the problem, unbalance load, and fail when that server dies. Use them only as a stop-gap.

### 14.3 Load balancing: how requests are spread

A **load balancer** receives each request and picks a server. Two levels exist: **Layer 4** balances TCP connections without reading them (fast, simple); **Layer 7** reads HTTP, so it can route by path or header, terminate TLS and retry (Nginx, HAProxy, cloud load balancers; swe.09 section 7).

The main algorithms:

| Algorithm | Idea | Good when | Weak when |
|---|---|---|---|
| **Round robin** | 1, 2, 3, 1, 2, 3... | requests cost about the same | some requests are far heavier |
| **Weighted round robin** | bigger servers get more turns | servers of different size | same as above |
| **Least connections** | send to the server with the fewest requests in flight | requests vary a lot in duration | needs the balancer to track state |
| **Random** | pick any | simple and surprisingly decent with many servers | unlucky streaks with few servers |
| **IP / key hash** | the same client or key always lands on the same server | caching per server, sticky behaviour | uneven spread, painful when servers are added (see 14.4) |

Compare three of them on identical traffic: 3 servers, each handling one request at a time, 3% of requests are slow (400 ms) and the rest take 10 ms. All numbers are simulated milliseconds; the random seeds are fixed, so the result is repeatable.

```python run
import random


def simulate(policy, n=20_000, servers=3, mean_gap=10.0):
    rng = random.Random(7)                                  # same traffic for every policy
    jobs, t = [], 0.0
    for _ in range(n):
        t += rng.expovariate(1 / mean_gap)
        jobs.append((t, 400.0 if rng.random() < 0.03 else 10.0))
    pick = random.Random(1)
    free_at = [0.0] * servers
    in_flight = [[] for _ in range(servers)]
    turn = 0
    latencies = []
    for arrive, duration in jobs:
        for s in range(servers):
            in_flight[s] = [f for f in in_flight[s] if f > arrive]
        if policy == "round robin":
            s, turn = turn % servers, turn + 1
        elif policy == "random":
            s = pick.randrange(servers)
        else:                                               # least connections
            s = min(range(servers), key=lambda k: len(in_flight[k]))
        start = max(arrive, free_at[s])
        free_at[s] = start + duration
        in_flight[s].append(free_at[s])
        latencies.append(free_at[s] - arrive)
    latencies.sort()
    q = lambda p: latencies[int(p * (len(latencies) - 1))]
    return q(0.50), q(0.95), q(0.99)


print(f"{'policy':20}{'p50':>8}{'p95':>9}{'p99':>9}   (milliseconds of waiting + work)")
for policy in ("round robin", "random", "least connections"):
    p50, p95, p99 = simulate(policy)
    print(f"{policy:20}{p50:8.1f}{p95:9.1f}{p99:9.1f}")
```
```text
policy                   p50      p95      p99   (milliseconds of waiting + work)
round robin            143.7    935.4   1330.6
random                 157.5    976.2   1495.5
least connections       12.9    442.6    732.8
```

When some requests are heavy, counting what is *currently running* beats blind rotation by a wide margin. Round robin and random cannot see that one server is stuck on a 400 ms request, so they keep stacking new requests behind it; least connections sees the queue and sends work elsewhere. The difference is largest in the tail (p95, p99), which is what users complain about, so always compare balancing by percentiles and never by the average alone. (The gap is smaller when all requests cost about the same: then round robin is nearly as good and much simpler.)

Balancers also need **health checks** (stop sending to a dead server; swe.09 section 9) and **connection draining** (let in-flight requests finish before removing a server during a deploy).

### 14.4 Consistent hashing: spreading *data* so that adding a server moves little

Load balancing a stateless tier needs no memory of past requests. But when servers hold **data** (cache nodes, database shards), a key must always go to the same node. The obvious method is `node = hash(key) % number_of_nodes`. It works until the number changes:

```python run
import bisect
import hashlib


def h(text):
    return int(hashlib.md5(text.encode()).hexdigest(), 16)


class Ring:
    """Consistent hashing: nodes sit on a circle (many virtual points each); a key belongs to the next point."""

    def __init__(self, nodes, vnodes=100):
        self.points = sorted((h(f"{n}#{i}"), n) for n in nodes for i in range(vnodes))
        self.hashes = [p for p, _ in self.points]

    def node_for(self, key):
        return self.points[bisect.bisect(self.hashes, h(key)) % len(self.points)][1]


keys = [f"user:{i}" for i in range(20_000)]
three, four = ["A", "B", "C"], ["A", "B", "C", "D"]

mod_before = {k: three[h(k) % 3] for k in keys}
mod_after = {k: four[h(k) % 4] for k in keys}
ring3, ring4 = Ring(three), Ring(four)
ring_before = {k: ring3.node_for(k) for k in keys}
ring_after = {k: ring4.node_for(k) for k in keys}

moved = lambda a, b: sum(a[k] != b[k] for k in keys) / len(keys)
print(f"adding a 4th node with hash % N      : {moved(mod_before, mod_after):6.1%} of keys move")
print(f"adding a 4th node with a hash ring   : {moved(ring_before, ring_after):6.1%} of keys move")
print("ideal (only the new node's share)    :  25.0%")

for vnodes in (1, 100):
    ring = Ring(four, vnodes)
    share = {n: 0 for n in four}
    for k in keys:
        share[ring.node_for(k)] += 1
    print(f"keys per node with {vnodes:3} virtual point(s) each:", share)
```
```text
adding a 4th node with hash % N      :  74.9% of keys move
adding a 4th node with a hash ring   :  24.0% of keys move
ideal (only the new node's share)    :  25.0%
keys per node with   1 virtual point(s) each: {'A': 640, 'B': 272, 'C': 8034, 'D': 11054}
keys per node with 100 virtual point(s) each: {'A': 5200, 'B': 5002, 'C': 5002, 'D': 4796}
```

With `hash % N`, going from 3 to 4 nodes remaps about three quarters of all keys; for a cache that means three quarters of lookups suddenly miss and hit the database together (a stampede, swe.08 section 6). A **hash ring** moves only about the new node's fair share. **Virtual nodes** (many points per server on the ring) are what keep the shares even: with one point each, the split is lumpy. This idea underlies Redis Cluster-like sharding, Cassandra, DynamoDB, memcached client libraries and CDNs.

### 14.5 What about the database tier?

The stateless app tier scales by cloning. The database tier cannot, because it holds the truth. That is the subject of section 15.

### Try it: why did the servers get uneven?

You add servers to the pool behind IP-hash balancing, and one server suddenly gets twice the traffic of the others. Give two possible reasons.

<details><summary>Answer</summary>

(1) **Skewed clients**: many users share one public IP (an office, a mobile carrier's NAT), so IP-hash sends them all to the same server. (2) **No virtual nodes / simple modulo**: with `hash % N`, changing N reshuffles users, and small N gives uneven shares. Better: balance on connections (least-connections) for stateless apps, and use consistent hashing with virtual nodes when affinity is really needed.

</details>

## 15. Scaling the data tier: replicas, partitions and CAP

### 15.1 The order in which to reach for tools

The database is the hardest part to scale. Try the cheap options first, in this order, and stop as soon as the numbers are healthy:

1. **Fix queries and indexes** (swe.03). Most "we need to scale" problems are a missing index.
2. **Cache** repeated reads (swe.08).
3. **Bigger machine** (more RAM so the working set fits in memory, faster disks).
4. **Read replicas**: copies that serve reads. Section 15.2.
5. **Move work off the request path**: queues, summary tables, search index.
6. **Partition (shard)** the data across several primaries. Section 15.4. This is the expensive one: do it last.

### 15.2 Read replicas and replication lag

A **replica** is a copy of the **primary** database, kept up to date by shipping the primary's changes to it. All writes go to the primary; reads can go to replicas, multiplying read capacity. Most products read far more than they write, so this fits.

The catch: replication is usually **asynchronous**. A write is acknowledged by the primary at once and arrives at the replica a moment later (milliseconds normally, seconds or more under load). During that gap a replica returns **old data**. The famous symptom: *a user saves their profile, the page reloads, and shows the old profile*.

```python run
class Cluster:
    """A primary and one replica; changes reach the replica `lag` seconds later."""

    def __init__(self, lag):
        self.primary, self.replica, self.lag, self.in_transit = {}, {}, lag, []

    def write(self, key, value, now):
        self.primary[key] = value
        self.in_transit.append((now + self.lag, key, value))

    def _apply_due(self, now):
        for item in [i for i in self.in_transit if i[0] <= now]:
            self.in_transit.remove(item)
            self.replica[item[1]] = item[2]

    def read_replica(self, key, now):
        self._apply_due(now)
        return self.replica.get(key)


db = Cluster(lag=0.3)
db.write("title", "old title", now=0.0)
db.read_replica("title", now=1.0)                          # everyone has caught up

db.write("title", "new title", now=2.0)                    # the user saves the form...
print("t=2.05  page reloads from replica :", db.read_replica("title", now=2.05))

# Fix: for a short window after a user's own write, read that user's data from the primary.
last_write = {"ana": 2.0}
def read_for(user, key, now, window=5.0):
    if now - last_write.get(user, -999) < window:
        return db.primary[key]                              # read-your-writes
    return db.read_replica(key, now)

print("t=2.05  same read with the fix    :", read_for("ana", "title", 2.05))
print("t=9.00  window over, replica again:", read_for("ana", "title", 9.0))
```
```text
t=2.05  page reloads from replica : old title
t=2.05  same read with the fix    : new title
t=9.00  window over, replica again: new title
```

The fix is called **read-your-writes** consistency. Other techniques: send a write's **version or log position** to the client and have the replica wait until it has caught up to that position; route sensitive reads (balance after a payment) always to the primary; or accept staleness where it is harmless (a product list, a count).

Also: replicas give **availability** (promote one if the primary dies, a process called failover) but failover has its own risks: writes acknowledged by the dead primary but not yet copied are lost, and a "split brain" (two primaries) must never happen. Use the database's managed failover rather than inventing it.

### 15.3 Consistency, in plain words

| Level | Promise | Example |
|---|---|---|
| **Strong** (linearizable) | every read sees the latest completed write | a single database primary; a bank balance |
| **Read-your-writes** | *you* see your own writes | profile edits |
| **Monotonic reads** | you never see time go backwards | a feed that does not "un-show" a post |
| **Eventual** | if writes stop, all copies become equal, at some point | likes counter, search index, replicas |

Stronger guarantees cost latency and availability. Choose per feature: the checkout needs strong consistency; the "people viewing this" badge does not.

### 15.4 Partitioning (sharding)

When one primary cannot hold the data or the write rate, **split the data** across several primaries by a **shard key**. Each shard holds a slice and handles its writes.

| Strategy | How | Good | Bad |
|---|---|---|---|
| **Range** | users A to F on shard 1, G to M on shard 2... or by date | range scans are cheap | hot spots: all new writes land on the newest range |
| **Hash** | `hash(key) % N` or a hash ring | even spread | range queries hit every shard; resharding hurts (14.4) |
| **Directory** | a lookup table says which shard owns which key | total flexibility | the lookup is a new bottleneck and single point of failure |

Choosing the shard key is the central decision. Good keys are **high-cardinality**, **evenly used**, and appear in **most queries**. For Taskboard, `project_id` is natural (a project's tasks live together), but one gigantic customer would make a **hot shard**; `task_id` spreads evenly but "list a project's tasks" would then query every shard.

What you lose when you shard:

- **Cross-shard queries and joins** become application logic or are impossible.
- **Cross-shard transactions** are not available (back to sagas, section 12.5).
- **Unique ids** need a scheme that is globally unique (section 16 shows one).
- **Resharding** (adding shards) is a project in itself; plan the ring or a large fixed number of logical shards from day one.

Many products never need sharding. A single PostgreSQL primary with replicas, good indexes and a cache carries a very large number of users. Treat sharding as a response to a measured limit.

### 15.5 CAP: what happens when the network splits

Distributed data stores have several copies, and the network between them can break. The **CAP theorem** says that when a network **P**artition occurs, a system must choose between:

- **C**onsistency: every read gets the latest write, or an error. To be sure, a node on the minority side must **refuse** to answer.
- **A**vailability: every request to a working node gets an answer, even if it may be **stale**, and writes are accepted on both sides.

Partitions are not optional in real networks, so the real choice is **C or A *during* a partition**. When the network is healthy you have both. Watch the choice in a three-node store split into {A, B} and {C}. Each write carries a timestamp, and on healing the newest write wins ("last write wins"):

```python run
class Unavailable(Exception):
    pass


class Store:
    def __init__(self, mode):
        self.mode, self.clock = mode, 0
        self.nodes = {n: ("v0", 0) for n in "ABC"}                 # (value, timestamp)
        self.reachable = {n: set("ABC") for n in "ABC"}           # who each node can talk to

    def partition(self):
        self.reachable = {"A": set("AB"), "B": set("AB"), "C": {"C"}}

    def write(self, node, value):
        self.clock += 1
        peers = self.reachable[node]
        if self.mode == "CP" and len(peers) < 2:                   # needs a majority (2 of 3)
            raise Unavailable(f"{node} cannot reach a majority, refusing the write")
        for peer in peers:
            self.nodes[peer] = (value, self.clock)

    def heal(self):
        newest = max(self.nodes.values(), key=lambda v: v[1])      # last write wins
        self.nodes = {n: newest for n in self.nodes}
        self.reachable = {n: set("ABC") for n in "ABC"}


for mode in ("CP", "AP"):
    s = Store(mode)
    s.partition()
    print(f"--- {mode}: network splits into {{A,B}} and {{C}}")
    for node, value in (("A", "written at A"), ("C", "written at C")):
        try:
            s.write(node, value)
            print(f"  write at {node}: accepted")
        except Unavailable as e:
            print(f"  write at {node}: REFUSED ({e})")
    s.heal()
    print("  after healing, every node holds:", s.nodes["A"][0])
```
```text
--- CP: network splits into {A,B} and {C}
  write at A: accepted
  write at C: REFUSED (C cannot reach a majority, refusing the write)
  after healing, every node holds: written at A
--- AP: network splits into {A,B} and {C}
  write at A: accepted
  write at C: accepted
  after healing, every node holds: written at C
```

- **CP** refused the write on the minority side: the user gets an error, but no data is ever lost or contradictory.
- **AP** accepted both writes. After healing, last-write-wins kept one and **silently discarded the other**: a lost update. AP systems need conflict handling (timestamps, version vectors, or merge rules like counters and sets that combine).

Neither is "better". Choose from the business: **money, inventory, unique usernames** want C (an error is better than selling the last seat twice); **shopping carts, likes, presence, feeds** often prefer A.

**PACELC** extends the idea: *if there is a Partition, choose Availability or Consistency; Else (normal operation) choose Latency or Consistency.* Even without partitions, waiting for all replicas to confirm a write (consistency) is slower than answering at once (latency). That is the replica-lag trade-off of 15.2 in one sentence.

Where do well-known systems sit? A single PostgreSQL primary with synchronous replicas leans CP. Cassandra and DynamoDB (default settings) lean AP and let you tune consistency per query. Redis with replicas is AP-ish (acknowledged writes can be lost on failover). Treat this as a rough guide; each product has settings that move it.

### 15.6 Where Taskboard sits

Taskboard on one SQLite file is a single node: it has no partitions to survive, and it is strongly consistent. To grow: move to PostgreSQL (primary + replica), add read-your-writes routing for the person who just edited, keep the outbox in the primary's transaction, and move on only when measurements say so. That is a perfectly respectable architecture for a product with tens of thousands of users.

### Try it: pick C or A

For each feature choose consistency or availability during a network partition, and say why: (a) transferring money between two accounts; (b) the "like" counter on a post; (c) reserving a seat on a flight; (d) the list of "online now" users.

<details><summary>Answer</summary>

(a) **Consistency**: refuse rather than create or lose money. (b) **Availability**: an approximate count that converges later is fine; use counters that merge. (c) **Consistency**: double-selling a seat is worse than an error message ("try again"); some airlines deliberately overbook and compensate later, which is a business-level answer, not a technical one. (d) **Availability**: stale presence is harmless and expected.

</details>


## 16. Worked design 1: a URL shortener

A URL shortener (`https://sho.rt/aZ3kP9x` redirects to a long address) is the classic first system design because it is small, but every part of the method appears in it. We follow the eight steps from section 13.1.

### 16.1 Requirements

| Kind | Requirement |
|---|---|
| Functional | Create a short code for a long URL. Redirect a short code to its URL. Optional: custom alias, expiry date, click counts. |
| Non-functional | Redirects must be **fast** (p95 under 50 ms) and **highly available** (a dead link on a printed flyer is forever). Creating links may be slightly slower. Codes must be unique. |
| Out of scope | User accounts, link editing, a dashboard. |

### 16.2 Estimates

Assume 100 million new links a month, kept 5 years, and 100 redirects per created link.

```python run
new_per_month = 100_000_000
writes_per_sec = new_per_month / (30 * 86_400)
reads_per_sec = writes_per_sec * 100
records = new_per_month * 12 * 5
bytes_per_record = 500                     # code + long URL + dates + some slack
print(f"create rate      : {writes_per_sec:8,.0f} per second on average, about {writes_per_sec * 3:,.0f} at peak")
print(f"redirect rate    : {reads_per_sec:8,.0f} per second on average, about {reads_per_sec * 3:,.0f} at peak")
print(f"records in 5 yrs : {records:,}")
print(f"storage in 5 yrs : {records * bytes_per_record / 1e12:.1f} TB before replicas and indexes")

length = 1
while 62 ** length < records:
    length += 1
print(f"code length      : {length} characters of base62 cover {62 ** length:,} codes (need {records:,})")
```
```text
create rate      :       39 per second on average, about 116 at peak
redirect rate    :    3,858 per second on average, about 11,574 at peak
records in 5 yrs : 6,000,000,000
storage in 5 yrs : 3.0 TB before replicas and indexes
code length      : 6 characters of base62 cover 56,800,235,584 codes (need 6,000,000,000)
```

Conclusions: writes are tiny (tens per second), **reads dominate** (thousands per second), the data is a few terabytes of simple key-value rows, and a 6-character code is enough *if codes are handed out without waste*. This is a **read-heavy, key-value** workload: perfect for caching.

### 16.3 API and data model

```text
POST /links          { "url": "https://example.com/a/very/long/path", "alias": "mine" (optional), "expires": "2027-01-01" (optional) }
                     -> 201 { "code": "aZ3kP9", "short_url": "https://sho.rt/aZ3kP9" }
GET  /{code}         -> 302 Location: https://example.com/a/very/long/path     (or 404 / 410 if expired)
```

```text
links(code PRIMARY KEY, url, created_at, expires_at)        one lookup by code: key-value shaped
clicks(code, at, ...)                                       written asynchronously (queue), never in the redirect path
```

The redirect asks exactly one question: "what is the URL for this code?" That is a lookup by primary key, the easiest query a database answers.

### 16.4 The deep dive: where do codes come from?

This is the one hard decision. Three options:

| Option | How | Problems |
|---|---|---|
| **Random code** | pick 6 random base62 characters; retry if taken | collisions get likelier as the table fills; every create needs a uniqueness check |
| **Hash of the URL** | take the first 6 characters of `sha256(url)` | collisions again, plus two users shortening the same URL get the same code (maybe fine, maybe a privacy leak) |
| **Counter, then base62** | a global counter gives 1, 2, 3...; convert the number to base62 | no collisions at all; needs a counter that works with many servers; codes are guessable |

First, how bad are random collisions? The **birthday paradox** says with `n` random codes in a space of `N` possible codes you expect about `n² / 2N` colliding pairs. Check the formula against a simulation:

```python run
import random

rng = random.Random(3)
n = 100_000
print(f"{n:,} random codes")
for length in (4, 5, 6):
    space = 62 ** length
    seen, collisions = set(), 0
    for _ in range(n):
        code = rng.randrange(space)
        collisions += code in seen
        seen.add(code)
    print(f"  {length} characters: space {space:>15,}   predicted about {n * n / (2 * space):8.1f} collisions   simulated {collisions}")
```
```text
100,000 random codes
  4 characters: space      14,776,336   predicted about    338.4 collisions   simulated 329
  5 characters: space     916,132,832   predicted about      5.5 collisions   simulated 4
  6 characters: space  56,800,235,584   predicted about      0.1 collisions   simulated 0
```

With 5 characters, only 100,000 links already collide about five times. Random codes need a uniqueness check on every insert and a retry loop. Not wrong, but not elegant.

The counter approach: convert a number to **base62** (digits, upper and lower case letters):

```python
# shortener.py
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"


def encode(n):
    if n == 0:
        return ALPHABET[0]
    digits = []
    while n:
        n, remainder = divmod(n, 62)
        digits.append(ALPHABET[remainder])
    return "".join(reversed(digits))


def decode(code):
    n = 0
    for ch in code:
        n = n * 62 + ALPHABET.index(ch)
    return n


class CentralCounter:
    """Stands in for one database row: `UPDATE counter SET next = next + :size RETURNING next - :size`."""

    def __init__(self):
        self.next = 1
        self.trips = 0

    def take_block(self, size):
        start, self.next = self.next, self.next + size
        self.trips += 1
        return start, start + size


class AppServer:
    """Hands out ids from a private block, so most creates never touch the central counter."""

    def __init__(self, name, central, block=1000):
        self.name, self.central, self.block = name, central, block
        self.current = self.end = 0

    def new_id(self):
        if self.current >= self.end:
            self.current, self.end = self.central.take_block(self.block)
        self.current += 1
        return self.current - 1
```

Try it. First the conversion, then three app servers creating links at the same time:

```python run
from shortener import AppServer, CentralCounter, decode, encode

for n in (0, 61, 62, 3_843, 125_000_000, 6_000_000_000):
    print(f"{n:>14,}  ->  {encode(n):>8}  ->  {decode(encode(n)):,}")
assert all(decode(encode(n)) == n for n in range(200_000))
print("round trip holds for the first 200,000 numbers")

central = CentralCounter()
servers = [AppServer(f"app-{i}", central, block=4) for i in (1, 2, 3)]
ids = []
for round_ in range(5):
    for s in servers:
        ids.append((s.name, s.new_id()))
print("ids handed out, in the order requests arrived:")
print("  ", ids)
print("all unique:", len({i for _, i in ids}) == len(ids), "| trips to the central counter:", central.trips, "for", len(ids), "ids")
```
```text
             0  ->         0  ->  0
            61  ->         z  ->  61
            62  ->        10  ->  62
         3,843  ->        zz  ->  3,843
   125,000,000  ->     8SUD2  ->  125,000,000
 6,000,000,000  ->    6Y3O5Y  ->  6,000,000,000
round trip holds for the first 200,000 numbers
ids handed out, in the order requests arrived:
   [('app-1', 1), ('app-2', 5), ('app-3', 9), ('app-1', 2), ('app-2', 6), ('app-3', 10), ('app-1', 3), ('app-2', 7), ('app-3', 11), ('app-1', 4), ('app-2', 8), ('app-3', 12), ('app-1', 13), ('app-2', 17), ('app-3', 21)]
all unique: True | trips to the central counter: 6 for 15 ids
```

Each app server asks the central counter for a **block** (4 here, 1,000 in real life) and then hands out ids from it with no coordination. Uniqueness is guaranteed; the price is gaps when a server restarts and loses the rest of its block (harmless, since we have 56 billion codes of length 6 and need 6 billion) and ids that are not strictly ordered in time (we do not need that). The central counter is touched once per 1,000 creates, so it is not a bottleneck. For availability, keep it in a replicated database, or give each data centre its own range.

**Guessable codes.** Counter codes are sequential: `aaa1`, `aaa2`, `aaa3`... Anyone can enumerate every short link, which is a privacy problem if links point to private documents. One cheap fix is to scramble the number with a **bijection**, a reversible one-to-one mapping, before encoding: multiply by a large number that is coprime with the size of the code space, modulo the size. No two inputs can produce the same output, so uniqueness is kept:

```python run
from math import gcd

from shortener import encode

LENGTH = 7
SPACE = 62 ** LENGTH
MULTIPLIER = 7_919_352_649_813                   # odd and not a multiple of 31, so coprime with 62**7
assert gcd(MULTIPLIER, SPACE) == 1, "the multiplier must be coprime with the size of the code space"
INVERSE = pow(MULTIPLIER, -1, SPACE)             # lets us go back


def scramble(n):
    return (n * MULTIPLIER) % SPACE


def unscramble(m):
    return (m * INVERSE) % SPACE


for n in (1, 2, 3, 4):
    print(f"id {n} -> {encode(scramble(n)).rjust(LENGTH, '0')}")
assert len({scramble(n) for n in range(1, 300_000)}) == 299_999, "a bijection never collides"
assert all(unscramble(scramble(n)) == n for n in range(1, 1000))
print("no collisions among 299,999 ids, and the mapping can be reversed")
```
```text
id 1 -> FQKKelp
id 2 -> UqefJXe
id 3 -> kGyzyJT
id 4 -> zhJKd5I
no collisions among 299,999 ids, and the mapping can be reversed
```

Be honest about what this is: **obscurity, not security**. Someone who sees enough codes could work out the multiplier. If link contents are truly secret, use random 128-bit tokens (longer URLs) or require authentication.

### 16.5 The high-level design

```text
 browser --> [CDN / edge cache: optional for very hot links]
                |
                v
          [Load balancer] --> [App servers (stateless)]
                                  |        |        \
                          cache hit?       |         `--(create)--> [Counter blocks]
                              |            |                              |
                         [Redis cache]   (miss)                           v
                                  \        v                       [links table, primary]
                                   `---> [links DB: primary + replicas, key = code]
                                  
         redirect path also emits  ->  [queue] -> [click-counting workers] -> [analytics store]
```

Reasoning, as it would be said out loud:

- **Reads dominate and are key lookups**, so put a **cache** in front. Link popularity is highly skewed (a few links get most traffic), so a cache of a few GB gives a very high hit ratio. Use cache-aside with a TTL (swe.08 section 4).
- **Use 302 (temporary) or 301 (permanent)?** `301` lets browsers cache the redirect forever: fewer requests to you, but you can neither count clicks nor change or expire the link. Most shorteners choose `302` for control, and accept the extra load.
- **Click counting is off the critical path**: the redirect puts an event on a queue and returns. If the queue is down, redirects must still work (fail open); counting can lag.
- **Writes go to the primary; reads can use replicas.** Replica lag matters in one place: right after creating a link, the creator opens it; if that read hits a lagging replica it gets 404. Use read-your-writes (section 15.2) or put the new link into the cache on creation.
- **Database growth**: 3 TB of key-value rows over 5 years fits on one big primary with replicas. If it ever does not, shard by a hash of `code` (section 15.4); every query already has the shard key, so sharding is clean.

### 16.6 Failure modes and abuse

| What goes wrong | Mitigation |
|---|---|
| Cache is cold after a restart: all reads hit the database | warm the hottest keys; stampede protection (swe.08 section 6) |
| A viral link is a hot key | the CDN or a local in-process cache in front of Redis |
| Counter database is down | servers keep serving ids from their current blocks; make the counter replicated |
| Malicious URLs (phishing, malware) | check against block lists at creation; rate limit creation per user and IP; take-down tool |
| Users create millions of links | quotas, authentication, expiry of unused links |
| Alias squatting (`/admin`, `/login`) | reserved-word list; validate aliases |
| Open redirect abuse | show an interstitial warning for unknown domains |

### 16.7 Trade-offs, said plainly

We chose counter blocks over random codes: no collision handling, at the cost of guessable (or merely obscured) codes and the need for one coordinated counter. We chose `302` over `301`: control and analytics, at the cost of load. We chose asynchronous click counting: fast redirects, at the cost of slightly stale numbers. We would revisit the counter if we needed multiple regions that cannot talk to each other (give each region its own prefix or range), and the cache design if the hit ratio fell below about 90%.

### Try it: custom aliases

Users may pick their own alias (`/spring-sale`). Which part of the design above must change, and what new problem appears?

<details><summary>Answer</summary>

Aliases live in the **same namespace** as generated codes, so two things can collide: a user's alias with a generated code (`/abc123` chosen as an alias, later generated by the counter), and two users choosing the same alias at once. Fixes: a `UNIQUE` constraint on `code` as the final referee (the second insert fails and the user is told "taken"); make generated codes use a character set or length aliases cannot use (for example generated codes are always exactly 7 characters and aliases are validated to be different, or aliases carry a prefix); and add a reserved-word list. The uniqueness check must be the database constraint, not a read-then-insert in Python (swe.07, idempotency and races).

</details>

## 17. Worked design 2: activity feed and notifications for Taskboard

This time the system is our own. Product asks: *"Show each user a feed of what happened in their projects, with an unread badge, and send e-mail or push notifications for the things they care about."* You already built the first ingredient, the **outbox of domain events** (section 9). Now design the rest.

### 17.1 Requirements

| Kind | Requirement |
|---|---|
| Functional | A feed of events (task created, assigned, completed) for the projects a user belongs to, newest first, paginated. An unread count. Notifications by e-mail and push, with per-user preferences. |
| Non-functional | The feed opens in under 200 ms. Notifications may arrive seconds late but **must not be lost** and must not be sent twice. Muting must take effect quickly. |
| Scale assumption | 2 million users, projects of up to 50,000 members, 5 million events a day. |

### 17.2 The central question: fan-out on write or on read?

An event happens in a project with M members. Each member's feed must show it. Two ways:

- **Fan-out on read** ("pull"): store each event **once**. When Ana opens her feed, query the events of all projects she belongs to, merge, sort, take the first 20.
- **Fan-out on write** ("push"): when an event happens, **copy** a pointer into an inbox row for each of the M members. Reading is then a simple "my inbox, newest first".

Build both on SQLite and measure. 1,000 users, 100 projects, each user in 3 projects (so about 30 members per project), 20,000 events:

```python run
import random
import sqlite3
import time

rng = random.Random(5)
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE members (user_id INT, project_id INT, PRIMARY KEY (user_id, project_id));
CREATE TABLE events  (id INTEGER PRIMARY KEY, project_id INT, text TEXT);
CREATE TABLE inbox   (user_id INT, event_id INT, PRIMARY KEY (user_id, event_id));
""")
USERS, PROJECTS, EVENTS = 1000, 100, 20_000
members_of = {}
for user in range(USERS):
    for project in rng.sample(range(PROJECTS), 3):
        db.execute("INSERT INTO members VALUES (?, ?)", (user, project))
        members_of.setdefault(project, []).append(user)
db.execute("CREATE INDEX members_by_project ON members (project_id, user_id)")
db.execute("CREATE INDEX events_by_project ON events (project_id, id)")

# --- writing: strategy B stores 1 row per event; strategy A also stores 1 row per member ---
start = time.perf_counter()
db.executemany("INSERT INTO events (project_id, text) VALUES (?, ?)",
               [(rng.randrange(PROJECTS), f"event {i}") for i in range(EVENTS)])
write_read_strategy = time.perf_counter() - start

start = time.perf_counter()
inbox_rows = [(u, event_id) for event_id, project in db.execute("SELECT id, project_id FROM events")
              for u in members_of[project]]
db.executemany("INSERT INTO inbox VALUES (?, ?)", inbox_rows)
write_extra = time.perf_counter() - start

# --- reading: the newest 20 items for a user ---
FEED_ON_WRITE = """SELECT e.id FROM inbox i JOIN events e ON e.id = i.event_id
                   WHERE i.user_id = ? ORDER BY i.event_id DESC LIMIT 20"""
FEED_ON_READ = """SELECT id FROM events
                  WHERE project_id IN (SELECT project_id FROM members WHERE user_id = ?)
                  ORDER BY id DESC LIMIT 20"""
for user in range(0, USERS, 50):
    assert db.execute(FEED_ON_WRITE, (user,)).fetchall() == db.execute(FEED_ON_READ, (user,)).fetchall()

def time_reads(sql, reads=1000):
    start = time.perf_counter()
    for i in range(reads):
        db.execute(sql, (i % USERS,)).fetchall()
    return (time.perf_counter() - start) / reads * 1000

print(f"events written                      : {EVENTS:>9,}")
print(f"extra inbox rows for fan-out on write: {len(inbox_rows):>9,}  ({len(inbox_rows) / EVENTS:.0f} rows per event)")
print(f"write time, store events only        : {write_read_strategy * 1000:8.0f} ms")
print(f"write time, extra inbox fan-out      : {write_extra * 1000:8.0f} ms")
print(f"read one feed, fan-out on read       : {time_reads(FEED_ON_READ):8.3f} ms")
print(f"read one feed, fan-out on write      : {time_reads(FEED_ON_WRITE):8.3f} ms")
```
```text
events written                      :    20,000
extra inbox rows for fan-out on write:   599,352  (30 rows per event)
write time, store events only        :       24 ms
write time, extra inbox fan-out      :      572 ms
read one feed, fan-out on read       :    0.013 ms
read one feed, fan-out on write      :    0.009 ms
```

Both strategies returned identical feeds (the assertion checks it). Read the numbers honestly:

- With 30 members per project, **both reads are fast**, and fan-out on write costs 30 times more rows and a noticeable write time for a benefit you cannot feel. At this scale the simple design (read-time) wins.
- Now extrapolate. One event in a project of **50,000 members** means 50,000 inbox rows; 5 million events a day with an average of even 500 members is 2.5 billion rows a day. Fan-out on write explodes. Meanwhile a user in 200 projects makes the read-time query merge 200 sources.

Typical solutions in large systems combine both (**hybrid**): fan out on write for ordinary projects (small M, so cheap and reads are instant), and *skip* the fan-out for huge projects, merging their recent events at read time. The decision rule is a threshold on M, chosen from measurements.

| | Fan-out on read | Fan-out on write |
|---|---|---|
| Write cost | 1 row per event | M rows per event |
| Read cost | grows with the number of projects a user follows | constant, simple |
| Storage | small | large (M copies of a pointer) |
| Mute / leave project | instant (just stop querying) | must delete or filter inbox rows |
| Best for | few sources per user, huge audiences | many reads, bounded audiences |

### 17.3 Notifications

Notifications are not the feed. They are **reactions** with extra rules, which is why they fit the event + outbox pattern: the Taskboard domain publishes `TaskAssigned`; a notification handler decides what to do.

```text
 Taskboard app --(same transaction)--> [outbox] --dispatcher--> [queue] --> [Notification worker]
                                                                                |
                         +------------- decide ---------------------------------+
                         |   who should hear about it?  (assignee, watchers)
                         |   do their preferences allow it? (mute, quiet hours)
                         |   already notified for this event? (dedupe key = event id + user + channel)
                         |   too many recently? (batch into a digest, rate limit)
                         v
                  [Channel adapters]  e-mail provider | push service | in-app inbox row
                         |
                         +--> on failure: retry with backoff, then dead-letter (swe.08)
```

Design decisions and their reasons:

| Decision | Choice | Why |
|---|---|---|
| Trigger | domain events through the outbox | cannot be lost, cannot announce a rolled-back change |
| Delivery guarantee | at-least-once with a **dedupe key** per (event, user, channel) | exactly-once does not exist across systems; idempotency gives the same effect |
| Preferences | stored per user, read by the worker at send time | a mute takes effect on the next send, not after a deploy |
| Channels | one small adapter per channel with the same interface | adding SMS is one new class, not a change in the pipeline |
| Bursts | rate limit per user, collapse into a digest ("5 tasks were assigned to you") | one bad import must not send 500 e-mails |
| Slow providers | each adapter has its own queue, timeout and circuit breaker (section 12) | a dead push service must not delay e-mails |
| Unread count | a counter per user updated when inbox rows are added, repaired by a periodic recount | counting rows on every page load does not scale |
| Ordering | per user, by event id; late delivery is acceptable | strict global order is expensive and not needed |

### 17.4 Failure modes

| Failure | Result | Mitigation |
|---|---|---|
| Worker crashes after sending, before marking done | duplicate delivery | dedupe key; provider idempotency header |
| E-mail provider outage | backlog grows | retries with backoff; alert on queue age (swe.08 section 15); circuit breaker |
| Huge project, one event | 50,000 notifications at once | batch, rate limit, spread over minutes |
| Preferences service slow | notifications stall | cache preferences with a short TTL; default to "send" or "hold" per channel, decided in advance |
| Poison event (bad payload) | retried for ever | max attempts, dead-letter queue, alert |
| User deleted / address bounced | repeated failures | suppression list updated from bounce events |

### 17.5 Trade-offs, said plainly

We chose the outbox over publishing straight to a broker: slower by a few hundred milliseconds, but no lost or phantom events and no new infrastructure. We chose hybrid fan-out: more code than either extreme, justified only if measured project sizes vary widely (if every project has fewer than 100 members, use fan-out on read and stop). We chose at-least-once plus dedupe keys over exactly-once: duplicates are possible but harmless. We would revisit the whole design if notifications needed to be **real time** (seconds, to a browser): that adds a push channel (WebSocket or Server-Sent Events, swe.05) with a connection-holding tier, which scales very differently from request/response servers.

### Try it: one huge project

A single project has 20,000 members and produces 100 events a day. How many inbox rows does fan-out on write create per day for that one project? What would you do about it?

<details><summary>Answer</summary>

`100 events × 20,000 members = 2,000,000` inbox rows a day, from **one** project, which is 66,000 times the work of a 30-member project's single event stream and would dominate the whole system. Use the hybrid: choose a threshold (say 1,000 members) above which a project is **not** fanned out. For those projects, store the event once and merge the project's recent events into each member's feed at read time. The merge costs a little at read time but only for the few members' large projects they follow, and the write cost stays at one row per event.

</details>

## 18. Writing it down: design documents and decision records

Design in your head is design you cannot review, remember or hand over. Two short documents cover most needs.

### 18.1 The design document

For anything bigger than a few days of work, write 1 to 3 pages **before** coding. A reader should understand the problem, your choice, and why not the alternatives. A template that works:

```text
Title, author, date, status (draft / reviewed / accepted)

1. Problem          What hurts, for whom, with evidence (numbers, incidents, a failing test).
2. Goals / non-goals What this must achieve. What it deliberately does NOT do.
3. Background       Only what a new reader needs.
4. Proposed design  Diagram + the key decisions in plain words (API, data, flow).
5. Alternatives     At least two, and why each lost.
6. Risks and failure modes   What happens when X dies? What is the rollback?
7. Rollout plan     Steps small enough to ship and undo one at a time.
8. Open questions   Honest list of what you do not know yet.
```

Good design documents are *short*, have a diagram, and name alternatives. The "Alternatives" section is the most valuable: it shows that you did not pick the first idea.

**Diagrams.** Draw what runs and who calls whom, as in the sketches in this chapter. The **C4 model** (Simon Brown) gives vocabulary for zoom levels: *context* (your system and the people and systems around it), *containers* (the separately running parts: web app, database, worker), *components* (modules inside one container), *code* (rarely drawn). Most designs need only the first two. Text diagrams like the ones here live next to the code and show up in diffs. Tools such as Mermaid or draw.io are fine; keep their source files in the repository, not only the picture.

### 18.2 The architecture decision record (ADR)

A design document explains a change. An **ADR** records one *decision* in a few lines, and is never deleted: if you change your mind you write a new ADR that supersedes the old one. In a year, when someone asks "why do we have an outbox?", the answer is in the repository.

The format (Michael Nygard's) has four parts: **Status**, **Context** (the forces and the pain), **Decision**, **Consequences** (good and bad). We add **Alternatives** because it is the most useful part. Here are three real ADRs for the Taskboard work in this chapter. They are files in `docs/adr/`:

```text
# docs/adr/0001-unit-of-work-per-request.md
# ADR 0001: One unit of work per request

## Status
Accepted

## Context
All requests shared one global SQLite connection. A request that failed after an
insert but before commit left the insert pending, and the next successful request
committed it (test_failed_email_leaves_no_half_saved_task, failing before the change).
Concurrent requests could also roll back each other's work.

## Decision
Every use case opens its own `SqliteUnitOfWork` (own connection, own transaction).
Services call `uow.commit()` once at the end; leaving the `with` block always rolls
back whatever was not committed.

## Consequences
+ A failed request cannot affect another request.
+ Services can be tested with a fake unit of work that models rollback.
- One connection per request (cheap for SQLite; use a pool for PostgreSQL).
- Services must remember to call `commit()`; forgetting it saves nothing, which tests notice.

## Alternatives
- Keep the shared connection and add try/rollback in each route: fixes the orphan row,
  not the interleaving, and every route must remember it.
- Adopt SQLAlchemy sessions: the same pattern with more machinery than this project needs.
```

```text
# docs/adr/0002-email-through-an-outbox.md
# ADR 0002: Send e-mail from an outbox, not from the request

## Status
Accepted

## Context
Services sent e-mail before commit. A rolled-back assignment still e-mailed the
assignee; sending after commit lost the e-mail when the provider failed and made
clients retry (creating duplicate tasks).

## Decision
Tasks record domain events. The service writes them to an `outbox` table in the same
transaction as the change. A dispatcher delivers pending rows, one transaction each,
with an idempotency key `outbox-<id>`. Failures leave the row pending.

## Consequences
+ No e-mail for rolled-back changes; no lost e-mail; a failing provider no longer fails requests.
+ The outbox is the seam for future consumers (webhooks, search, a notification service).
- Delivery is at-least-once, so consumers must be idempotent.
- E-mail arrives a moment after the response; "why was this sent?" needs a search for the handler.
- Pending rows need monitoring (age of the oldest pending item).

## Alternatives
- Send before commit / after commit: both rejected (see Context).
- A message broker now: no second consumer yet; revisit when one exists.
```

```text
# docs/adr/0003-stay-a-modular-monolith.md
# ADR 0003: Stay a modular monolith; do not split services yet

## Status
Accepted

## Context
Product asked about moving notifications into their own service. Current load:
about 25 requests per second at peak, one team of four, one database, one deployment.

## Decision
Keep one deployable. Keep `domain`, `services`, `notifications`, `dispatch` separated by
import rules enforced in `tests/test_architecture.py`. The outbox payload is treated as a
public contract: fields are added, never renamed or removed without a new event version.

## Consequences
+ No network failures, no distributed transactions, one pipeline to maintain.
+ A later split has a ready seam: the outbox and the event format.
- Notification code cannot be scaled or deployed independently until we split.
- Discipline is needed: the architecture test must stay green and be extended with new modules.

## Alternatives
- Extract notifications now: rejected, no independent scaling need and no second team.

## Revisit when
Notification sending needs a different scaling profile, or a second team owns it.
```

Look at them as files. Note how each ADR starts from **pain with evidence**, exactly like the pain log in section 3:

```bash run
ls docs/adr
echo "-----"
grep -n "^## " docs/adr/0002-email-through-an-outbox.md
```
```text
0001-unit-of-work-per-request.md
0002-email-through-an-outbox.md
0003-stay-a-modular-monolith.md
-----
3:## Status
6:## Context
11:## Decision
16:## Consequences
23:## Alternatives
```

### 18.3 Habits that keep documents alive

- Put docs **in the repository** next to the code, reviewed in the same pull request.
- Write an ADR when a decision is *hard to reverse* or *surprising*. Not for every function.
- When a decision is replaced, mark the old ADR `Superseded by ADR 00NN` instead of editing history.
- A document nobody updates is worse than none. Prefer a few short ones that stay true.

### Try it: ADR or not?

Which of these deserves an ADR? (a) Using `dataclass` instead of a hand-written class. (b) Choosing PostgreSQL over SQLite for production. (c) Naming the e-mail function `send_email`. (d) Making the outbox payload an external contract.

<details><summary>Answer</summary>

**(b) and (d).** Both are hard to reverse and affect many people and systems later, and someone will certainly ask "why?". (a) and (c) are cheap to change and obvious in code; documenting them is noise.

</details>

## 19. Project: refactor the task API where it actually hurts, and document why

### 19.1 The task

Take the task-management API you built in swe.05 (or Taskboard from this chapter if you do not have one). **Do not** apply all the layers. Instead, follow the discipline of this chapter and refactor only where the code hurts, then explain your choices in writing.

### 19.2 Steps

1. **Safety net.** Make sure you have tests that talk to the API from the outside (HTTP and a temporary database). Note how many tests there are and how long they take. If there are none, write them first for every rule; this is the most valuable hour of the project.
2. **Pain log.** Explore your code for the pains in section 3: a rule in several places (use `grep`), a failure that leaves half-saved data (write a test that makes it fail), slow tests with heavy setup (time them), SQL mixed into rules (count the lines). Record **at least three** in `docs/pain-log.md` with evidence, using the table format of section 3.4. If you find fewer than three, say so honestly and explain why your code does not need more structure. That is a valid result.
3. **Choose remedies.** For each pain, choose the smallest remedy from the ladder (section 1.4). Decide in writing what you will *not* do, for example "no repository: only one table, no rules in SQL".
4. **Refactor in small steps.** One remedy at a time. After each step the full test suite must pass. Write the failing test for the pain **first** and watch it turn green. Each step is a separate commit.
5. **Add an architecture test** that enforces at least one dependency rule you introduced (section 10.2).
6. **Write ADRs**: one for each layer you added, and one for a layer you deliberately did **not** add. Four sections each: Status, Context, Decision, Consequences.
7. **Write a one-page design note, "10× traffic"** (section 13): requirements, an estimate of your current and 10× load, a diagram, the first bottleneck you expect, and the first thing you would change. Include one CAP/consistency decision for one feature.
8. **Measure the bill**: lines of code and number of files before and after (section 10.3), and the time of your test suite. Put the numbers in your README.

### 19.3 Acceptance checklist

| Check | Done when |
|---|---|
| Behaviour preserved | The original API tests pass, unchanged except for setup fixtures |
| Pain removed | Each logged pain has a test that failed before and passes now |
| Layers justified | Every layer maps to a pain-log row; at least one "not added" decision is written down |
| Dependencies enforced | An architecture test fails if an inner layer imports an outer one |
| Failure handled | A test proves that a failed request leaves no half-saved data |
| Documents exist | `docs/pain-log.md`, at least 2 ADRs, a one-page 10× design note |
| Costs reported | Before and after file/line counts and test time in the README |

You can check the mechanical parts with a small script. It does not judge quality, only that the evidence exists. First, the pain log of this chapter's Taskboard, in the required format:

```text
# docs/pain-log.md
# Pain log

| # | Pain | Evidence | Remedy |
|---|---|---|---|
| P1 | Rule 3 (max 3 open tasks) enforced in 1 of 3 entry points | test_assign_by_patch_respects_wip_limit, test_reopen_respects_wip_limit failed | Service layer, one check function (section 4) |
| P2 | A failed request corrupted a later one | test_failed_email_leaves_no_half_saved_task failed | Unit of work, one connection per request (section 7) |
| P3 | Testing one rule needed HTTP and a database | a few milliseconds per HTTP create vs microseconds for the pure rule | Repository + fake, domain model (sections 5, 6, 8) |
| P4 | Rules, SQL, mail and JSON in one 95-line file | 16 SQL statements in main.py | Services, repository, domain (sections 4 to 8) |
| P5 | E-mail sent inside the transaction | script showing an e-mail for a rolled-back assignment | Domain events and outbox (section 9) |
```

```python
# check_refactor.py
"""Mechanical checks for the refactoring project. Run from the project root."""
import pathlib
import re
import subprocess
import sys

problems = []


def need(ok, message):
    print(("PASS  " if ok else "FAIL  ") + message)
    if not ok:
        problems.append(message)


adrs = sorted(pathlib.Path("docs/adr").glob("0*.md"))
need(len(adrs) >= 2, f"at least 2 ADRs in docs/adr (found {len(adrs)})")
for f in adrs:
    text = f.read_text()
    missing = [h for h in ("Status", "Context", "Decision", "Consequences")
               if not re.search(rf"^##\s+{h}\b", text, re.M)]
    need(not missing, f"{f.name} has Status, Context, Decision, Consequences" +
         (f" (missing: {missing})" if missing else ""))

rows = []
log = pathlib.Path("docs/pain-log.md")
if log.exists():
    for line in log.read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 4 and re.fullmatch(r"P\d+", cells[0]):
            rows.append(cells)
need(len(rows) >= 3, f"pain log has at least 3 rows (found {len(rows)})")
need(all(len(r[2]) >= 10 for r in rows) and bool(rows), "every pain has evidence (not just 'it is messy')")
need(all(r[3] for r in rows) and bool(rows), "every pain names a remedy")

need(pathlib.Path("tests/test_architecture.py").exists(), "an architecture test exists")

result = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "tests"],
                        capture_output=True, text=True)
need(result.returncode == 0, "the full test suite passes")
print()
print("all mechanical checks passed" if not problems else f"{len(problems)} check(s) failed")
sys.exit(1 if problems else 0)
```

```bash run
python check_refactor.py
```
```text
PASS  at least 2 ADRs in docs/adr (found 3)
PASS  0001-unit-of-work-per-request.md has Status, Context, Decision, Consequences
PASS  0002-email-through-an-outbox.md has Status, Context, Decision, Consequences
PASS  0003-stay-a-modular-monolith.md has Status, Context, Decision, Consequences
PASS  pain log has at least 3 rows (found 5)
PASS  every pain has evidence (not just 'it is messy')
PASS  every pain names a remedy
PASS  an architecture test exists
PASS  the full test suite passes

all mechanical checks passed
```

Passing the script means the *evidence exists*. Whether the decisions were wise is for a reviewer, or for you in three months, to judge by reading the ADRs.

### 19.4 Stretch goals

- Add a second **handler** for `TaskAssigned` (a webhook, written as a fake HTTP client). It should take one new file and no change to the services.
- Write a **second repository implementation** (for example a CSV-file or in-memory one) and prove it with the contract tests of section 6.3.
- Add the **read-your-writes** rule from section 15.2 to a pretend replica in your fakes.
- Write the design document for "Taskboard 100× bigger" using the template in section 18.1 and the estimation script of section 13.3.

### 19.5 Questions to answer in your README

1. Which pain hurt most, and what evidence convinced you it was real?
2. Which layer did you decide **not** to add, and what would make you add it?
3. What did the refactoring cost in lines and files? Was it worth it?
4. If the traffic grew tenfold tomorrow, what breaks first, and what is your first move?

## 20. Common traps

1. **Layers before pain**: a repository, a service and an event bus for a three-route CRUD app (1.2, 10.4).
2. **No safety net**: refactoring without tests that describe the outside behaviour, then not knowing what broke (2.3).
3. **Mixing a refactor with a behaviour change** in one step, so nobody can tell which caused a failure (4.3).
4. **A shared global connection** or session; transaction ownership left to convention (3.1, 7.1).
5. **Services that know HTTP** (importing FastAPI, raising `HTTPException`) so no other caller can reuse them (4.2).
6. **God services and anonymous "managers"** with dozens of methods and no clear use cases (4.5).
7. **Fakes that lie**: an in-memory repository that returns the same object, so a forgotten `save` goes unnoticed; no contract tests (6.3).
8. **A commit inside the repository**, which destroys all-or-nothing behaviour across several writes (7, Try it).
9. **A domain object that queries the database**, dragging I/O back into the rules (8.2).
10. **Sending e-mail (or calling any external system) inside the transaction**, before or after the commit (9.1).
11. **Assuming exactly-once delivery**; no idempotency key, so a crash after sending duplicates the effect (9.2, 17.3).
12. **Silent unknown events**: a dispatcher that drops events with no handler without a log or an explicit "ignore" (9.5).
13. **Architecture rules that live only in people's heads**; no test that fails when an inner layer imports an outer one (10.2).
14. **Splitting into microservices because the monolith is messy**: you get a messy network, a distributed monolith (11.4).
15. **A shared database between "separate" services**, so a schema change breaks several teams at once (11.4, 11.5).
16. **Network calls without a timeout**, or with the library default you never checked (12.1).
17. **Retries at every layer** (retry storms), retries of non-idempotent writes, retries without jitter (12.2).
18. **Designing for imaginary scale**: no estimate, so a cluster for 2 requests per second (13.3).
19. **State in app servers** (sessions in memory, files on local disk) that blocks horizontal scaling (14.2).
20. **`hash % N` to place data**, so adding a node moves most keys (14.4).
21. **Comparing load balancers by the average** latency instead of the tail (14.3).
22. **Reading from a replica right after a write** with no read-your-writes rule (15.2).
23. **Picking consistency or availability per product instead of per feature**; every data type gets the same setting (15.5).
24. **Sharding early**, or with a shard key that creates hot spots or forces cross-shard queries (15.4).
25. **Fan-out on write for huge audiences** (a 50,000-member project means 50,000 writes per event) (17.2).
26. **Guessable, sequential public identifiers** treated as if they were secrets (16.4).
27. **No written reasons**: decisions that nobody can explain a year later; ADRs that are edited instead of superseded (18.2).

## 21. Collected traps

| If you see... | The cause is usually... | Look at |
|---|---|---|
| The same business rule fixed in two routes last week | the rule is copy-pasted; no single home | 3.1, 4 |
| A later request saves data from an earlier failed one | shared connection, no owner of the transaction | 3.1, 7 |
| Unit tests need a database file and 40 lines of setup | rules entangled with storage | 5, 8 |
| The fast fake-based tests pass but production fails | the fake differs from the real repository; no contract tests | 6.3 |
| Data is "saved" in a test but the real code loses it | forgotten `save`/`commit`; fake shares objects or never rolls back | 6.3, 7.3 |
| An e-mail was sent for a change that was rolled back | side effect inside the transaction | 9.1 |
| Duplicate e-mails after a crash or restart | at-least-once delivery without an idempotency key | 9.2, 9.6 |
| Pending outbox rows keep growing | dispatcher down, a poison item, no alert on age | 9.5, 17.4 |
| A "quick fix" imported `sqlite3` into the services | no architecture test | 10.2 |
| Services need FastAPI to be imported | the dependency arrow points outwards | 10.2 |
| After splitting, every release needs all services deployed together | distributed monolith | 11.4 |
| A downstream outage takes the whole app down | no timeout, no circuit breaker, thread pool exhausted | 12.1, 12.3 |
| Database load multiplies during an outage | retry storm; retries at several layers | 12.2 |
| Requests randomly log users out behind a load balancer | sessions stored in each server's memory | 14.2 |
| Cache hit ratio collapses after adding a cache node | modulo placement instead of consistent hashing | 14.4 |
| A user saves a form and sees the old values | reading from a lagging replica | 15.2 |
| Two users got the same "unique" thing during a network split | availability chosen where consistency was needed | 15.5 |
| One shard is on fire while others are idle | hot shard from a poor shard key | 15.4 |
| Writes explode when a big group posts | fan-out on write for a huge audience | 17.2 |
| Nobody knows why the system is built this way | decisions never recorded | 18.2 |

## 22. Summary

- **Architecture** is the set of decisions that are expensive to change. Good architecture keeps the cost of change low where change is likely. Both the big ball of mud and the architecture astronaut are failures.
- **Pain first, layer second.** Before adding a layer write down the concrete pain, the evidence, how you will know it is fixed, and what the layer costs. Keep a pain log. If you cannot point at the pain, do not add the layer.
- A **safety net of outside-in tests** makes refactoring safe: the outside behaviour must not change, and a behaviour change is made as its own visible step.
- **Service layer**: one function per use case; no HTTP knowledge; domain errors that the web layer maps to status codes; each rule in one place. It removes duplicated, drifting rules.
- **Repository**: a collection-like object with questions in business words that hides storage. It removes SQL from rule code and makes fast fakes possible. **Contract tests** keep fakes honest. It is not free; skip it for one-table apps with no rules.
- **Unit of work**: one object per use case that owns the connection and transaction, hands out repositories, commits once and always rolls back what was not committed. It removes half-saved data and cross-request interference. SQLAlchemy sessions and Django's `atomic` are the same idea.
- **Domain model**: rules live in objects next to the data they protect; facts are passed in so the domain stays pure and trivially testable. Do not force it where there are no rules.
- **Events and the outbox**: save the intention in the same transaction as the change, deliver it afterwards. No side effects for rolled-back changes, nothing lost, at-least-once delivery made safe with idempotency keys. Events are also the seam for later extraction.
- **The dependency rule**: arrows point towards the domain; one composition root wires the concrete parts; an `ast`-based test enforces it. Count the bill (files, lines) and stop at the right row of the ladder.
- **Monolith, modular monolith, microservices**: a split turns function calls into network calls with timeouts, partial failure and no shared transaction. Start with a modular monolith with clean seams; split for people or load reasons; migrate with a strangler fig. Avoid the distributed monolith.
- **Talking to other services**: always a timeout (know the library default), limited retries with backoff and jitter at **one** layer for idempotent operations, a circuit breaker, planned fallbacks, sagas only when you must.
- **System design method**: requirements (including non-functional), estimates, API, data model, diagram, deep dive, bottlenecks and failures, trade-offs said plainly. Put numbers on everything; most products need far less scale machinery than people expect.
- **Scaling**: keep the app tier stateless and clone it behind a load balancer (compare by percentiles; least connections wins with uneven requests); use consistent hashing with virtual nodes for data placement. For the data tier go in order: queries and indexes, cache, bigger machine, read replicas (with read-your-writes), queues and summaries, and only then sharding with a careful shard key.
- **Consistency and CAP**: under a partition you choose between consistency (refuse) and availability (answer, maybe stale, reconcile later); choose per feature (money and unique seats want C; likes and presence want A). PACELC adds the everyday latency-versus-consistency trade-off.
- **Worked designs**: a URL shortener (read-heavy key-value; counter blocks with base62 beat random codes; cache and asynchronous analytics) and a feed with notifications (fan-out on read vs write chosen by measured audience sizes; outbox, dedupe keys, rate limits and per-channel isolation).
- **Write it down**: a short design document with alternatives, and ADRs (Status, Context, Decision, Consequences) kept in the repository and superseded, never rewritten.

Next: the 25 problems for this module practise diagnosing pain from code and test output, placing rules in the right layer, tracing a failed request through a unit of work, judging fakes and contract tests, reading an outbox log, estimating load, comparing load balancing and sharding choices, reasoning about replica lag and CAP, and building a design from a short brief; the project is to refactor your task API only where it hurts and document why.
