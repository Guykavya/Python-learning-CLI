import pytest

from solution import NotFound, RuleViolation, assign_task, dispatch

NOW = "2026-01-01T00:00:00"
EMAILS = {1: "ana@example.com", 2: "ben@example.com", 3: "cy@example.com", 4: "bounce@example.com"}


class MailError(Exception):
    pass


class IdempotentMailer:
    """Like a real provider: refuses 'bounce' addresses and ignores an idempotency key it has already seen."""

    def __init__(self):
        self.sent, self.keys = [], set()

    def send(self, to, subject, key):
        if to.startswith("bounce"):
            raise MailError(f"provider rejected {to}")
        if key in self.keys:
            return
        self.keys.add(key)
        self.sent.append((to, subject))


@pytest.fixture
def mailer():
    return IdempotentMailer()


@pytest.fixture
def handlers(mailer):
    def on_task_assigned(uow, item):
        p = item.payload
        mailer.send(EMAILS[p["assignee_id"]], f"Task assigned: {p['title']}", key=f"outbox-{item.id}")

    return {"TaskAssigned": on_task_assigned}


# ----------------------------------------------------------------------------- publishing, in the same transaction
def test_assigning_saves_the_task_and_publishes_one_event(world):
    world.add_task("Ship it")
    task = assign_task(world.uow(), 1, 1, NOW)
    assert task.assignee_id == 1 and world.task(1).assignee_id == 1, "The assignment must be committed."
    assert world.pending() == [("TaskAssigned", {"task_id": 1, "assignee_id": 1, "title": "Ship it"})], \
        f"One TaskAssigned event with the payload of drain_events, written to the outbox; got {world.pending()}"


def test_the_returned_task_has_no_pending_events_left(world):
    world.add_task()
    assert assign_task(world.uow(), 1, 1, NOW).events == [], "The events were drained into the outbox: do not publish them twice."


def test_the_request_sends_no_email(world, mailer):
    world.add_task()
    assign_task(world.uow(), 1, 2, NOW)
    assert mailer.sent == [], "assign_task only records the intention; the dispatcher sends later."


def test_a_rule_violation_publishes_nothing(world):
    world.add_task()
    with pytest.raises(RuleViolation, match="not a member"):
        assign_task(world.uow(), 1, 3, NOW)                       # user 3 belongs to project 2 only
    assert world.pending() == [], "No outbox row for a change that never happened."
    assert world.task(1).assignee_id is None


def test_the_work_in_progress_limit_still_holds(world):
    for i in range(3):
        world.add_task(f"busy{i}", assignee_id=1)
    loose = world.add_task("loose")
    with pytest.raises(RuleViolation, match="3 open tasks"):
        assign_task(world.uow(), loose, 1, NOW)
    assert world.pending() == []


def test_an_unknown_task_is_not_found(world):
    with pytest.raises(NotFound):
        assign_task(world.uow(), 99, 1, NOW)
    assert world.pending() == []


def test_a_failing_commit_leaves_neither_a_half_saved_task_nor_an_event(world):
    world.add_task()
    world.store.fail_next_commit = True
    with pytest.raises(RuntimeError, match="disk full"):
        assign_task(world.uow(), 1, 1, NOW)
    assert world.task(1).assignee_id is None, "The task change must not survive a failed commit."
    assert world.pending() == [], "And neither may the outbox row: they are saved together or not at all."


def test_commit_is_called_once_at_the_end(world):
    world.add_task()
    calls = []
    uow = world.uow()
    real_commit = uow.commit
    uow.commit = lambda: (calls.append(1), real_commit())[1]
    assign_task(uow, 1, 1, NOW)
    assert calls == [1], f"Call commit() exactly once, after the task AND the outbox rows are written; it was called {len(calls)} times"


# ----------------------------------------------------------------------------- delivering
def test_dispatch_delivers_exactly_once(world, mailer, handlers):
    world.add_task("Ship it")
    assign_task(world.uow(), 1, 1, NOW)
    assert dispatch(world.uow, handlers, NOW) == (1, 0)
    assert mailer.sent == [("ana@example.com", "Task assigned: Ship it")]
    assert dispatch(world.uow, handlers, NOW) == (0, 0), "A delivered item must not be delivered again."
    assert world.pending() == []


def test_the_sent_time_is_recorded(world, handlers):
    world.add_task()
    assign_task(world.uow(), 1, 1, NOW)
    dispatch(world.uow, handlers, "2026-02-02T00:00:00")
    assert world.sent_at() == ["2026-02-02T00:00:00"], "mark_sent receives the `now` of the dispatch."


def test_a_failed_delivery_stays_pending_and_is_retried(world, mailer, handlers):
    world.add_task("for bounce")
    assign_task(world.uow(), 1, 4, NOW)                           # bounce@example.com is rejected by the provider
    assert dispatch(world.uow, handlers, NOW) == (0, 1)
    assert [k for k, _ in world.pending()] == ["TaskAssigned"], "The item must wait, not vanish."
    EMAILS[4] = "fixed@example.com"                               # the address is corrected
    try:
        assert dispatch(world.uow, handlers, NOW) == (1, 0)
    finally:
        EMAILS[4] = "bounce@example.com"
    assert mailer.sent == [("fixed@example.com", "Task assigned: for bounce")]


def test_one_bad_item_does_not_block_the_others(world, mailer, handlers):
    for title, user in (("a", 1), ("b", 4), ("c", 2)):
        world.add_task(title)
        assign_task(world.uow(), world.store.data["next_task_id"] - 1, user, NOW)
    assert dispatch(world.uow, handlers, NOW) == (2, 1), "The bounce in the middle fails; the items around it are delivered."
    assert sorted(m[0] for m in mailer.sent) == ["ana@example.com", "ben@example.com"]
    assert [p["title"] for _, p in world.pending()] == ["b"], "Only the failed item remains pending."


def test_each_item_has_its_own_transaction(world):
    world.add_task("x")
    assign_task(world.uow(), 1, 1, NOW)

    def writes_then_fails(uow, item):
        uow.outbox.add("Echo", {"copy_of": item.id}, NOW)           # a write inside the item's unit of work
        raise RuntimeError("handler failed after writing")

    assert dispatch(world.uow, {"TaskAssigned": writes_then_fails}, NOW) == (0, 1)
    assert [k for k, _ in world.pending()] == ["TaskAssigned"], "A failed item's unit of work is rolled back: its writes must not be kept."


def test_a_crash_after_sending_does_not_send_twice(world, mailer, handlers):
    world.add_task("x")
    assign_task(world.uow(), 1, 1, NOW)

    def send_then_crash(uow, item):
        handlers["TaskAssigned"](uow, item)
        raise RuntimeError("power cut before 'mark sent' was committed")

    assert dispatch(world.uow, {"TaskAssigned": send_then_crash}, NOW) == (0, 1)
    assert len(mailer.sent) == 1 and len(world.pending()) == 1, "Sent, but still pending: at-least-once."
    assert dispatch(world.uow, handlers, NOW) == (1, 0)
    assert len(mailer.sent) == 1, "The item is delivered AGAIN, and the idempotency key outbox-<id> stops the second e-mail."


def test_an_event_without_a_handler_is_marked_sent(world):
    world.add_task()
    assign_task(world.uow(), 1, 1, NOW)
    assert dispatch(world.uow, {}, NOW) == (1, 0), "Nobody reacts to this event kind: mark it sent so that it does not block the queue."
    assert world.pending() == []


def test_the_limit_is_respected_and_order_is_kept(world, handlers, mailer):
    for title in ("first", "second", "third"):
        world.add_task(title)
        assign_task(world.uow(), world.store.data["next_task_id"] - 1, 1 if title != "third" else 2, NOW)
    assert dispatch(world.uow, handlers, NOW, limit=2) == (2, 0)
    assert [m[1] for m in mailer.sent] == ["Task assigned: first", "Task assigned: second"], "Oldest first."
    assert len(world.pending()) == 1


def test_a_rolled_back_request_followed_by_a_dispatch_sends_nothing(world, mailer, handlers):
    world.add_task()
    with pytest.raises(RuleViolation):
        assign_task(world.uow(), 1, 3, NOW)
    assert dispatch(world.uow, handlers, NOW) == (0, 0)
    assert mailer.sent == [], "The first failure of chapter 9.1 (an e-mail for a rolled-back change) can no longer happen."
