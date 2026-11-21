import inspect

import pytest
from fastapi.testclient import TestClient

import solution
from solution import InvalidInput, NotFound, RuleViolation, create_app, create_task


def count(conn, table="tasks"):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


# ----------------------------------------------------------------------------- the service, called directly (no FastAPI)
def test_creates_an_unassigned_task(conn, mailer):
    result = create_task(conn, mailer, 1, "Write docs")
    assert result == {"id": 1, "title": "Write docs", "status": "todo", "assignee_id": None}, f"Return the task as a dict; got {result}"
    row = conn.execute("SELECT project_id, title, status, assignee_id FROM tasks WHERE id = 1").fetchone()
    assert tuple(row) == (1, "Write docs", "todo", None)
    assert [r["action"] for r in conn.execute("SELECT action FROM audit")] == ["created"], "One audit line 'created'."
    assert mailer.sent == [], "No assignee: no e-mail."


def test_title_is_trimmed_and_validated(conn, mailer):
    assert create_task(conn, mailer, 1, "   x  ")["title"] == "x", "Trim the title."
    for bad in ("", "   ", "a" * 121):
        with pytest.raises(InvalidInput):
            create_task(conn, mailer, 1, bad)
    assert create_task(conn, mailer, 1, "a" * 120)["title"] == "a" * 120, "120 characters is allowed."


def test_title_is_checked_before_the_project(conn, mailer):
    with pytest.raises(InvalidInput):
        create_task(conn, mailer, 99, "   ")


def test_unknown_project(conn, mailer):
    with pytest.raises(NotFound):
        create_task(conn, mailer, 99, "x")


def test_assignee_must_be_a_member(conn, mailer):
    with pytest.raises(RuleViolation, match="member"):
        create_task(conn, mailer, 1, "x", assignee_id=3)
    assert count(conn) == 0, "A refused request must not have inserted anything."


def test_wip_limit(conn, mailer):
    for i in range(3):
        create_task(conn, mailer, 1, f"t{i}", assignee_id=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        create_task(conn, mailer, 1, "t3", assignee_id=1)
    assert create_task(conn, mailer, 1, "t3", assignee_id=2)["assignee_id"] == 2, "Other people are unaffected."


def test_done_tasks_do_not_count(conn, mailer):
    create_task(conn, mailer, 1, "old", assignee_id=1)
    conn.execute("UPDATE tasks SET status = 'done' WHERE id = 1")
    for i in range(3):
        create_task(conn, mailer, 1, f"t{i}", assignee_id=1)


def test_assigning_sends_exactly_one_email(conn, mailer):
    create_task(conn, mailer, 1, "Ship it", assignee_id=1)
    assert mailer.sent == [("ana@example.com", "New task: Ship it")], f"One e-mail to the assignee; got {mailer.sent}"


def test_the_service_does_not_commit(conn, mailer):
    create_task(conn, mailer, 1, "not saved yet")
    conn.rollback()
    assert count(conn) == 0, "The service must not call commit(): the caller owns the transaction."


def test_the_service_knows_nothing_about_http():
    source = inspect.getsource(create_task)
    for word in ("HTTPException", "status_code", "JSONResponse", "fastapi", "commit("):
        assert word not in source, f"create_task must not mention {word!r}: the web layer translates, the service only holds the rules."


# ----------------------------------------------------------------------------- the outside did not change
@pytest.fixture
def client(db_path, mailer):
    return TestClient(create_app(db_path, mailer), raise_server_exceptions=False)


def make(client, title="Write docs", assignee=None, project=1):
    return client.post(f"/projects/{project}/tasks", json={"title": title, "assignee_id": assignee})


def test_http_create(client, mailer):
    r = make(client, assignee=1)
    assert r.status_code == 201 and r.json() == {"id": 1, "title": "Write docs", "status": "todo", "assignee_id": 1}, r.text
    assert mailer.sent == [("ana@example.com", "New task: Write docs")]


def test_http_errors_are_translated_by_the_web_layer(client):
    assert make(client, title="   ").status_code == 422
    assert make(client, project=99).status_code == 404
    assert make(client, assignee=3).status_code == 409
    for i in range(3):
        assert make(client, title=f"t{i}", assignee=1).status_code == 201
    r = make(client, title="t3", assignee=1)
    assert r.status_code == 409 and "3 open tasks" in r.json()["detail"], r.text


def test_a_failing_mail_provider_saves_nothing(client, db_path):
    import sqlite3
    r = make(client, title="for bounce", assignee=4)
    assert r.status_code == 500, "The mailer raised: an unexpected error is a 500."
    assert sqlite3.connect(db_path).execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0, \
        "The route rolls back when the use case raises, so no orphan task is left."
