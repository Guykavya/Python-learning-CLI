import ast
import inspect
import re
import sqlite3
import time
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import solution
from solution import (ADR, PAIN_LOG, InvalidInput, NotFound, RuleViolation, SqliteUnitOfWork, Task, create_app, create_task,
                      get_task, list_tasks, update_task)


# ================================================================== the safety net: tests that talk HTTP (chapter 2.3, unchanged)
@pytest.fixture
def client(db_path, mailer):
    return TestClient(create_app(db_path, mailer), raise_server_exceptions=False)


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


def test_assigning_sends_one_email(client, mailer):
    make(client, title="Ship it", assignee=1)
    assert mailer.sent == [("ana@example.com", "New task: Ship it")]


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


def test_get_one_task(client):
    tid = make(client, title="one").json()["id"]
    assert client.get(f"/tasks/{tid}").json()["title"] == "one"
    assert client.get("/tasks/999").status_code == 404


# ================================================================== the three pains of chapter 3 (they fail on the monolith)
def fill_ana(client):
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
    fill_ana(client)
    r = client.patch(f"/tasks/{first}", json={"status": "todo"})
    assert r.status_code == 409, "reopening makes the task open again: that would be a 4th"


def test_failed_email_leaves_no_half_saved_task(client):
    r = make(client, title="for bounce", assignee=4)          # the mail provider rejects this address
    assert r.status_code == 500
    make(client, title="next")                                 # an unrelated, perfectly valid request
    titles = [t["title"] for t in client.get("/projects/1/tasks").json()]
    assert titles == ["next"], f"the failed request left traces behind: {titles}"


# ================================================================== the service layer, with a fake unit of work (no HTTP, no SQL)
def test_fourth_open_task_is_refused(fake_world, mailer):
    for i in range(3):
        create_task(fake_world.uow(), mailer, 1, f"t{i}", 1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        create_task(fake_world.uow(), mailer, 1, "t3", 1)


def test_assigning_an_existing_task_respects_the_limit(fake_world, mailer):
    for i in range(3):
        create_task(fake_world.uow(), mailer, 1, f"t{i}", 1)
    loose = create_task(fake_world.uow(), mailer, 1, "loose")
    with pytest.raises(RuleViolation, match="3 open tasks"):
        update_task(fake_world.uow(), mailer, loose.id, assignee_id=1)


def test_reopening_respects_the_limit(fake_world, mailer):
    old = create_task(fake_world.uow(), mailer, 1, "old", 1)
    update_task(fake_world.uow(), mailer, old.id, status="doing")
    update_task(fake_world.uow(), mailer, old.id, status="done")
    for i in range(3):
        create_task(fake_world.uow(), mailer, 1, f"t{i}", 1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        update_task(fake_world.uow(), mailer, old.id, status="todo")


def test_done_tasks_do_not_count_as_open(fake_world, mailer):
    first = create_task(fake_world.uow(), mailer, 1, "first", 1)
    update_task(fake_world.uow(), mailer, first.id, status="doing")
    update_task(fake_world.uow(), mailer, first.id, status="done")
    for i in range(3):
        create_task(fake_world.uow(), mailer, 1, f"t{i}", 1)                # 3 open + 1 done: fine


def test_reassigning_to_the_same_person_is_not_a_new_load(fake_world, mailer):
    tasks = [create_task(fake_world.uow(), mailer, 1, f"t{i}", 1) for i in range(3)]
    update_task(fake_world.uow(), mailer, tasks[0].id, assignee_id=1)       # no error


def test_title_rules_and_missing_project(fake_world, mailer):
    assert create_task(fake_world.uow(), mailer, 1, "  padded  ").title == "padded"
    with pytest.raises(InvalidInput):
        create_task(fake_world.uow(), mailer, 1, "   ")
    with pytest.raises(NotFound):
        create_task(fake_world.uow(), mailer, 99, "x")
    with pytest.raises(NotFound):
        get_task(fake_world.uow(), 99)


def test_audit_trail_has_one_line_per_change(fake_world, mailer):
    t = create_task(fake_world.uow(), mailer, 1, "x", 2)
    update_task(fake_world.uow(), mailer, t.id, status="doing")
    with fake_world.uow() as check:
        assert check.tasks.audit_for(t.id) == ["created", "status:doing"]


def test_a_failed_use_case_saves_nothing(fake_world, mailer):
    t = create_task(fake_world.uow(), mailer, 1, "x")
    uow = fake_world.uow()
    with pytest.raises(RuleViolation):                          # assign to Ben (fine), then an illegal move: the whole request fails
        update_task(uow, mailer, t.id, assignee_id=2, status="done")
    assert not uow.committed, "A failed use case must not commit."
    with fake_world.uow() as check:
        assert check.tasks.get(t.id).assignee_id is None, "the assignment must be rolled back too"
        assert check.tasks.audit_for(t.id) == ["created"], "no audit line for a rolled-back change"


def test_a_refused_request_sends_no_email(fake_world, mailer):
    for i in range(3):
        create_task(fake_world.uow(), mailer, 1, f"t{i}", 1)
    mailer.sent.clear()
    with pytest.raises(RuleViolation):
        create_task(fake_world.uow(), mailer, 1, "t3", 1)
    assert mailer.sent == [], "Check the rules BEFORE the e-mail."


def test_the_injected_mailer_is_used(fake_world, mailer):
    create_task(fake_world.uow(), mailer, 1, "Ship it", 1)
    t = create_task(fake_world.uow(), mailer, 1, "Fix it")
    update_task(fake_world.uow(), mailer, t.id, assignee_id=2)
    assert mailer.sent == [("ana@example.com", "New task: Ship it"), ("ben@example.com", "Task assigned: Fix it")]


def test_a_failing_mailer_leaves_no_task_behind(fake_world, mailer):
    from conftest import MailError                              # the mailer of the tests raises MailError for 'bounce' addresses
    with pytest.raises(MailError):
        create_task(fake_world.uow(), mailer, 1, "for bounce", 4)
    assert fake_world.store.data["tasks"] == {} and fake_world.store.data["audit"] == [], "The e-mail failed before commit: nothing may be saved."


def test_get_and_list(fake_world, mailer):
    a = create_task(fake_world.uow(), mailer, 1, "a")
    create_task(fake_world.uow(), mailer, 2, "elsewhere")
    update_task(fake_world.uow(), mailer, a.id, status="doing")
    assert get_task(fake_world.uow(), a.id).status == "doing"
    assert [t.title for t in list_tasks(fake_world.uow(), 1)] == ["a"]
    assert [t.title for t in list_tasks(fake_world.uow(), 1, "doing")] == ["a"] and list_tasks(fake_world.uow(), 1, "done") == []


def test_service_tests_run_in_well_under_half_a_second(fake_world, mailer):
    start = time.perf_counter()
    for _ in range(25):
        world = type(fake_world)()                                  # a fresh world each round
        for i in range(3):
            create_task(world.uow(), mailer, 1, f"t{i}", 1)
        with pytest.raises(RuleViolation):
            create_task(world.uow(), mailer, 1, "t3", 1)
        t = create_task(world.uow(), mailer, 1, "x")
        update_task(world.uow(), mailer, t.id, status="doing")
    assert time.perf_counter() - start < 0.5, "Rules tested with a fake unit of work need no database and no HTTP: 25 rounds must take far less than 0.5 s."


# ================================================================== the unit of work on a real file
def new_task(title="x", **kw):
    base = dict(id=None, project_id=1, title=title, status="todo", assignee_id=None, created_at="2026-01-01T00:00:00")
    return Task(**{**base, **kw})


def titles(path):
    with SqliteUnitOfWork(path) as check:
        return [t.title for t in check.tasks.list_for_project(1)]


def test_the_unit_of_work_commits_and_rolls_back(db_path):
    with SqliteUnitOfWork(db_path) as uow:
        uow.tasks.add(new_task("saved"))
        uow.commit()
    with SqliteUnitOfWork(db_path) as uow:
        uow.tasks.add(new_task("forgot to commit"))
    with pytest.raises(RuntimeError):
        with SqliteUnitOfWork(db_path) as uow:
            uow.tasks.add(new_task("doomed"))
            raise RuntimeError("boom")
    assert titles(db_path) == ["saved"], "Only the committed work survives; leaving the block always rolls back the rest."


def test_task_and_audit_line_are_one_transaction(db_path):
    with pytest.raises(RuntimeError):
        with SqliteUnitOfWork(db_path) as uow:
            t = uow.tasks.add(new_task("half"))
            uow.tasks.add_audit(t.id, "created", "now")
            raise RuntimeError("crash before commit")
    with SqliteUnitOfWork(db_path) as check:
        assert check.tasks.list_for_project(1) == [] and check.tasks.audit_for(1) == []


def test_each_use_opens_its_own_connection(db_path):
    uow = SqliteUnitOfWork(db_path)
    with uow:
        first = uow.conn
    with uow:
        second = uow.conn
    assert first is not second
    with pytest.raises(sqlite3.ProgrammingError):
        first.execute("SELECT 1")


# ================================================================== where the SQL and the HTTP live (the layers are real)
SERVICE_FUNCTIONS = (create_task, update_task, get_task, list_tasks)


@pytest.mark.parametrize("function", SERVICE_FUNCTIONS, ids=lambda f: f.__name__)
def test_services_know_nothing_about_sql_or_http(function):
    source = inspect.getsource(function)
    for word in ("execute(", "sqlite3", "HTTPException", "JSONResponse", "fastapi", "FastAPI", "conn."):
        assert word not in source, f"{function.__name__} mentions {word!r}: the service holds the rules; SQL belongs to the repository and HTTP to the routes."


def test_all_sql_lives_in_the_infrastructure_classes():
    tree = ast.parse(Path(solution.__file__).read_text(encoding="utf-8"))
    offenders = []
    for node in tree.body:
        if not isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        calls_sql = any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ("execute", "executescript", "executemany")
                        for n in ast.walk(node))
        allowed = (isinstance(node, ast.ClassDef) and "Sqlite" in node.name) or node.name == "connect"
        if calls_sql and not allowed:
            offenders.append(node.name)
    assert not offenders, f"These top-level definitions still contain SQL: {offenders}. Move it into repository classes (names containing 'Sqlite') or the connect() helper."


def test_the_routes_translate_domain_errors_in_one_place(client):
    app = client.app
    assert solution.DomainError in app.exception_handlers, "Register ONE exception handler for DomainError and keep HTTP codes out of the services."
    source = inspect.getsource(create_app)
    assert "HTTPException" not in source, "The routes no longer raise HTTPException: rules raise domain errors."


# ================================================================== the documents
def sections(text):
    found, current = {}, None
    for line in text.splitlines():
        match = re.match(r"^##\s+(\w+)\s*$", line)
        if match:
            current = match.group(1)
            found[current] = ""
        elif current:
            found[current] += line + "\n"
    return found


def test_the_adr_has_its_sections_with_content():
    assert isinstance(ADR, str) and ADR.strip(), "ADR must be a non-empty string (an architecture decision record in Markdown)."
    found = sections(ADR)
    for name in ("Status", "Context", "Decision", "Consequences", "Alternatives"):
        assert name in found, f"The ADR needs a '## {name}' section; found {sorted(found)}"
        needed = 6 if name == "Status" else 20                                # "Accepted" is a complete Status
        assert len(re.sub(r"\s", "", found[name])) >= needed, f"The '## {name}' section is empty or too short to say anything."
    assert ADR.lstrip().startswith("# "), "Start with a title line: '# ADR 0001: ...'"


def test_the_pain_log_maps_each_layer_to_its_pain():
    assert isinstance(PAIN_LOG, list) and len(PAIN_LOG) >= 3, "Write at least three rows: one pain for each layer you added."
    for row in PAIN_LOG:
        assert isinstance(row, dict) and {"pain", "evidence", "remedy"} <= set(row), f"Each row needs pain, evidence and remedy; got {row!r}"
        assert len(row["pain"]) >= 10 and len(row["evidence"]) >= 10, "Name the pain and give evidence you could re-check (a failing test, a count, a timing), not 'it is messy'."
    remedies = {row["remedy"] for row in PAIN_LOG}
    assert remedies <= {"service layer", "repository", "unit of work"}, f"remedy must be one of 'service layer', 'repository', 'unit of work'; got {sorted(remedies)}"
    assert remedies == {"service layer", "repository", "unit of work"}, f"Every layer needs a pain that justifies it; missing {sorted({'service layer', 'repository', 'unit of work'} - remedies)}"
