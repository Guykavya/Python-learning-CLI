import pytest

from solution import RuleViolation, Task


def task(status="todo", assignee=None, completed_at=None):
    return Task(1, 1, "t", status, assignee, "2026-01-01T00:00:00", completed_at)


# ----------------------------------------------------------------------------- assign
def test_assign_needs_membership():
    t = task()
    with pytest.raises(RuleViolation, match="not a member"):
        t.assign(3, is_member=False, open_count=0)
    assert t.assignee_id is None, "A refused assignment must not change the task."


def test_assign_refuses_a_full_person():
    t = task()
    with pytest.raises(RuleViolation, match="3 open tasks"):
        t.assign(1, is_member=True, open_count=3)
    assert t.assignee_id is None
    t.assign(1, is_member=True, open_count=2)
    assert t.assignee_id == 1, "With 2 open tasks there is room for a third."


def test_the_limit_is_a_parameter():
    with pytest.raises(RuleViolation, match="5 open tasks"):
        task().assign(1, is_member=True, open_count=5, limit=5)
    t = task()
    t.assign(1, is_member=True, open_count=4, limit=5)
    assert t.assignee_id == 1


def test_membership_is_checked_even_when_the_task_is_free_of_load():
    with pytest.raises(RuleViolation, match="not a member"):
        task(status="done").assign(3, is_member=False, open_count=0)


def test_assigning_a_done_task_is_free():
    t = task(status="done")
    t.assign(1, is_member=True, open_count=3)
    assert t.assignee_id == 1, "A done task adds no load: a full person may still be given it."


def test_assigning_to_the_same_person_is_free():
    t = task(assignee=1)
    t.assign(1, is_member=True, open_count=3)
    assert t.assignee_id == 1, "They already carry this task: nothing changes, so no free slot is needed."


def test_reassigning_an_open_task_to_a_full_person_is_refused():
    t = task(assignee=1)
    with pytest.raises(RuleViolation, match="3 open tasks"):
        t.assign(2, is_member=True, open_count=3)
    assert t.assignee_id == 1


# ----------------------------------------------------------------------------- status moves
def test_the_happy_flow_and_completed_at():
    t = task()
    t.start()
    assert t.status == "doing"
    t.finish("2026-02-02T00:00:00")
    assert (t.status, t.completed_at) == ("done", "2026-02-02T00:00:00"), "finish sets completed_at to `now`."
    t.reopen(open_count=0)
    assert (t.status, t.completed_at) == ("todo", None), "reopen clears completed_at."


def test_pause_goes_back_to_todo():
    t = task(status="doing")
    t.pause()
    assert t.status == "todo"


@pytest.mark.parametrize("status, method, args, target", [
    ("doing", "start", (), "doing"), ("done", "start", (), "doing"),
    ("todo", "pause", (), "todo"), ("done", "pause", (), "todo"),
    ("todo", "finish", ("now",), "done"), ("done", "finish", ("now",), "done"),
    ("todo", "reopen", (0,), "todo"), ("doing", "reopen", (0,), "todo"),
])
def test_wrong_status_is_refused_and_leaves_the_task_alone(status, method, args, target):
    t = task(status=status, completed_at="old" if status == "done" else None)
    before = (t.status, t.completed_at, t.assignee_id)
    with pytest.raises(RuleViolation, match=f"cannot move from {status} to {target}"):
        getattr(t, method)(*args)
    assert (t.status, t.completed_at, t.assignee_id) == before, "A refused move must not change the task."


# ----------------------------------------------------------------------------- reopen needs a free slot
def test_reopening_needs_a_free_slot():
    t = task(status="done", assignee=1, completed_at="x")
    with pytest.raises(RuleViolation, match="3 open tasks"):
        t.reopen(open_count=3)
    assert (t.status, t.completed_at) == ("done", "x"), "A refused reopen leaves the task done."
    t.reopen(open_count=2)
    assert t.status == "todo"


def test_reopening_an_unassigned_task_needs_no_slot():
    t = task(status="done", assignee=None)
    t.reopen(open_count=99)
    assert t.status == "todo", "Nobody's limit applies to an unassigned task."


def test_reopen_checks_the_status_first():
    t = task(status="todo", assignee=1)
    with pytest.raises(RuleViolation, match="cannot move from todo to todo"):
        t.reopen(open_count=3)


def test_the_limit_applies_to_reopen_too():
    t = task(status="done", assignee=1)
    with pytest.raises(RuleViolation, match="2 open tasks"):
        t.reopen(open_count=2, limit=2)
