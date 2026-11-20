import sqlite3
from contextlib import closing

import pytest

from solution import init_email_log, make_safe_handler

POINTS = [None, "start", "after-claim", "after-send", "after-record"]


def _log(path):
    with closing(sqlite3.connect(path)) as db:
        return db.execute("SELECT key, to_addr, state, provider_id FROM email_log").fetchall()


def test_no_crash(crash_run):
    provider, states, path = crash_run(init_email_log, make_safe_handler)
    assert len(provider.outbox) == 1, f"One job, no crash: exactly one e-mail, got {len(provider.outbox)}."
    assert states == ["done"]
    assert _log(path) == [("welcome:7", "ada@example.com", "sent", "msg-1")], \
        f"The log must hold one row: key 'welcome:<user_id>', the address, state 'sent' and the provider's message id; got {_log(path)}"


@pytest.mark.parametrize("point", POINTS)
def test_crash_at_every_point(crash_run, point):
    provider, states, _ = crash_run(init_email_log, make_safe_handler, point)
    assert len(provider.outbox) == 1, \
        f"Crash at {point!r}, then a retry: the user must get exactly ONE e-mail, got {len(provider.outbox)}. " \
        "Record intent before sending and pass idempotency_key=key to provider.send."
    assert states == ["done"], f"After the retry the job must be done; got {states}."


def test_crash_points_are_called(make_provider, crash_at, crash_type, tmp_path):
    path = str(tmp_path / "a.db")
    init_email_log(path)
    for point in POINTS[1:]:
        handler = make_safe_handler(path, make_provider(), crash_at(point))
        try:
            handler({"user_id": 99, "to": "x@example.com"}, {"id": 1})
        except crash_type:
            pass
        else:
            pytest.fail(f"The handler never called crash.hit({point!r}). Call it at exactly these points, in order: "
                        "'start', 'after-claim', 'after-send', 'after-record'.")
        with closing(sqlite3.connect(path, isolation_level=None)) as db:
            db.execute("DELETE FROM email_log")            # start the next point from an empty log


def test_lost_response(crash_run):
    provider, states, _ = crash_run(init_email_log, make_safe_handler, lose_response=True)
    assert len(provider.outbox) == 1, \
        "The provider sent the message but the answer was lost (ProviderTimeout). The retry must send the SAME key so nothing is sent twice."
    assert states == ["done"]


def test_enqueued_twice(crash_run):
    provider, states, _ = crash_run(init_email_log, make_safe_handler, duplicate_jobs=2)
    assert len(provider.outbox) == 1, \
        "Two jobs for the same user's welcome e-mail must send ONE e-mail: the key names the e-mail (welcome:<user_id>), not the job."
    assert states == ["done", "done"], "Both jobs finish: the second one sees 'sent' and returns."


def test_enqueued_twice_and_crash(crash_run):
    provider, states, _ = crash_run(init_email_log, make_safe_handler, "after-send", duplicate_jobs=2)
    assert len(provider.outbox) == 1 and states == ["done", "done"]


def test_key_reaches_the_provider(crash_run):
    provider, _, _ = crash_run(init_email_log, make_safe_handler)
    assert "welcome:7" in provider._by_key, "provider.send must receive idempotency_key='welcome:<user_id>'."


def test_different_users_each_get_one(make_provider, crash_at, tmp_path):
    path = str(tmp_path / "b.db")
    init_email_log(path)
    provider = make_provider()
    handler = make_safe_handler(path, provider, crash_at(None))
    for user_id, to in [(1, "a@example.com"), (2, "b@example.com"), (1, "a@example.com")]:
        handler({"user_id": user_id, "to": to}, {"id": user_id})
    assert sorted(m["to"] for m in provider.outbox) == ["a@example.com", "b@example.com"], \
        "Each user gets one welcome e-mail; a repeat for user 1 sends nothing."


def test_init_is_repeatable(tmp_path):
    path = str(tmp_path / "c.db")
    init_email_log(path)
    init_email_log(path)            # a second start of the worker must not fail
    assert _log(path) == []
