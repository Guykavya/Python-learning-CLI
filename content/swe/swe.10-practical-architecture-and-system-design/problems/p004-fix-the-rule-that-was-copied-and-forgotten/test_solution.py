import pytest

import solution
from solution import RuleViolation, create_task, update_task


@pytest.fixture(autouse=True)
def clear_mail():
    solution.SENT.clear()


def fill(conn, user=1, n=3):
    return [create_task(conn, 1, f"busy{i}", user)["id"] for i in range(n)]


def test_create_respects_the_limit(conn):
    fill(conn)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        create_task(conn, 1, "t3", 1)
    assert create_task(conn, 1, "t3", 2)["assignee_id"] == 2, "Other users are unaffected."


def test_assign_by_patch_respects_the_limit(conn):
    fill(conn)
    loose = create_task(conn, 1, "loose")["id"]
    with pytest.raises(RuleViolation, match="3 open tasks"):
        update_task(conn, loose, assignee_id=1)
    assert conn.execute("SELECT assignee_id FROM tasks WHERE id = ?", (loose,)).fetchone()[0] is None, "A refused assignment must not change the task."


def test_a_refused_assignment_sends_no_email_and_writes_no_audit(conn):
    fill(conn)
    loose = create_task(conn, 1, "loose")["id"]
    solution.SENT.clear()
    with pytest.raises(RuleViolation):
        update_task(conn, loose, assignee_id=1)
    assert solution.SENT == [], "The rule must be checked BEFORE the e-mail and the audit line."
    assert [r["action"] for r in conn.execute("SELECT action FROM audit WHERE task_id = ?", (loose,))] == ["created"]


def test_reopen_respects_the_limit(conn):
    old = create_task(conn, 1, "old", 1)["id"]
    update_task(conn, old, status="doing")
    update_task(conn, old, status="done")
    fill(conn)                                               # three OTHER open tasks
    with pytest.raises(RuleViolation, match="3 open tasks"):
        update_task(conn, old, status="todo")
    assert conn.execute("SELECT status FROM tasks WHERE id = ?", (old,)).fetchone()[0] == "done", "A refused reopen must leave the task done."


def test_reopen_works_when_there_is_room(conn):
    old = create_task(conn, 1, "old", 1)["id"]
    update_task(conn, old, status="doing")
    update_task(conn, old, status="done")
    fill(conn, n=2)
    result = update_task(conn, old, status="todo")
    assert result["status"] == "todo" and result["completed_at"] is None, "With 2 other open tasks there is a free slot."


def test_reopening_an_unassigned_task_needs_no_slot(conn):
    t = create_task(conn, 1, "nobody", None)["id"]
    update_task(conn, t, status="doing")
    update_task(conn, t, status="done")
    assert update_task(conn, t, status="todo")["status"] == "todo", "No assignee: nobody's limit applies."


def test_assigning_a_done_task_is_free(conn):
    fill(conn)
    t = create_task(conn, 1, "closed")["id"]
    update_task(conn, t, status="doing")
    update_task(conn, t, status="done")
    assert update_task(conn, t, assignee_id=1)["assignee_id"] == 1, "A done task adds no load: assigning it to a full person is allowed."


def test_assigning_to_the_same_person_is_free(conn):
    ids = fill(conn)
    assert update_task(conn, ids[0], assignee_id=1)["assignee_id"] == 1, "Re-assigning to the person who already has it changes nothing."


def test_assign_and_reopen_in_one_request_uses_the_new_assignee(conn):
    done = create_task(conn, 1, "closed")["id"]
    update_task(conn, done, status="doing")
    update_task(conn, done, status="done")
    fill(conn, user=2)                                       # Ben is full
    with pytest.raises(RuleViolation, match="3 open tasks"):
        update_task(conn, done, assignee_id=2, status="todo")


def test_reassigning_an_open_task_to_a_full_person_is_refused(conn):
    fill(conn, user=1)
    mine = create_task(conn, 1, "ben's", 2)["id"]
    with pytest.raises(RuleViolation, match="3 open tasks"):
        update_task(conn, mine, assignee_id=1)


def test_done_tasks_do_not_count_as_open(conn):
    first = create_task(conn, 1, "first", 1)["id"]
    update_task(conn, first, status="doing")
    update_task(conn, first, status="done")
    for i in range(3):
        create_task(conn, 1, f"t{i}", 1)                     # 3 open + 1 done: fine
    with pytest.raises(RuleViolation):
        create_task(conn, 1, "t3", 1)


def test_the_status_flow_is_unchanged(conn):
    t = create_task(conn, 1, "x")["id"]
    with pytest.raises(RuleViolation, match="cannot move from todo to done"):
        update_task(conn, t, status="done")
    assert update_task(conn, t, status="doing")["status"] == "doing"
    assert update_task(conn, t, status="todo")["status"] == "todo"
    update_task(conn, t, status="doing")
    done = update_task(conn, t, status="done")
    assert done["completed_at"] is not None
    with pytest.raises(RuleViolation, match="cannot move from done to doing"):
        update_task(conn, t, status="doing")


def test_emails_and_audit_are_unchanged(conn):
    t = create_task(conn, 1, "Ship it", 1)["id"]
    update_task(conn, t, assignee_id=2)
    update_task(conn, t, status="doing")
    assert solution.SENT == [("ana@example.com", "New task: Ship it"), ("ben@example.com", "Task assigned: Ship it")]
    assert [r["action"] for r in conn.execute("SELECT action FROM audit WHERE task_id = ? ORDER BY id", (t,))] == ["created", "assigned", "status:doing"]


def test_the_rule_is_written_once():
    import inspect
    source = inspect.getsource(solution)
    assert source.count("status != 'done'") == 1, \
        "The 'open task' query must exist exactly once (in _check_capacity): that is the whole point of one place for one rule."
