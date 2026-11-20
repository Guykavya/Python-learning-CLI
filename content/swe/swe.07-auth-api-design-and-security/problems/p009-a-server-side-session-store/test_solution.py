import re

import pytest

from solution import SessionStore


class Clock:
    def __init__(self, t=0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def store(clock):
    return SessionStore(clock)


def test_create_and_get(store):
    sid = store.create("asha")
    assert isinstance(sid, str) and len(sid) == 43 and re.fullmatch(r"[A-Za-z0-9_-]+", sid), \
        f"Use secrets.token_urlsafe(32) for the id (43 url-safe characters); got {sid!r}"
    assert store.get(sid) == "asha", "get() of a live session returns the user name."


def test_ids_are_unique_and_unrelated_to_the_user(store):
    ids = {store.create("asha") for _ in range(200)}
    assert len(ids) == 200, "Every create() needs a new random id, even for the same user."


@pytest.mark.parametrize("junk", [None, "", "nope", 123])
def test_unknown_ids_give_none(store, junk):
    store.create("asha")
    try:
        result = store.get(junk)
    except Exception as exc:
        pytest.fail(f"get({junk!r}) raised {type(exc).__name__}; unknown ids return None.")
    assert result is None, f"get({junk!r}) must be None, got {result!r}"


def test_idle_boundary(store, clock):
    sid = store.create("asha")
    clock.t = 1799
    assert store.get(sid) == "asha", "1799 s after the last use the session is alive (idle is 1800)."
    clock.t = 1799 + 1800
    assert store.get(sid) is None, "Exactly 1800 s after the last use the session is expired: use `>=`, not `>`."


def test_get_slides_the_idle_timer(store, clock):
    sid = store.create("asha")
    clock.t = 1700
    assert store.get(sid) == "asha"
    clock.t = 3400                       # 1700 s since the last get, 3400 since create
    assert store.get(sid) == "asha", "A successful get() must restart the idle timer (store the time of the last use)."


def test_failed_get_changes_nothing(store, clock):
    sid = store.create("asha")
    store.get("wrong-id")
    clock.t = 1800
    assert store.get(sid) is None, "An unrelated failed get() must not slide the timer of other sessions."


def test_absolute_limit_beats_activity(store, clock):
    sid = store.create("asha")
    for t in range(1000, 28800, 1000):
        clock.t = t
        assert store.get(sid) == "asha", f"At t={t} the session is active and younger than 8 h: it must be alive."
    clock.t = 28799
    assert store.get(sid) == "asha", "28799 s after creation, used 799 s ago: still alive."
    clock.t = 28800
    assert store.get(sid) is None, "At exactly 28800 s after CREATION the session must die even if it was just used (absolute timeout)."


def test_expired_session_is_deleted(store, clock):
    sid = store.create("asha")
    clock.t = 5000
    assert store.get(sid) is None
    clock.t = 5001
    assert store.get(sid) is None, "An expired session stays dead."
    assert sid not in repr(vars(store)), "Delete the row of an expired session when you find it."


def test_custom_limits(clock):
    s = SessionStore(clock, idle=10, absolute=25)
    sid = s.create("ravi")
    clock.t = 9
    assert s.get(sid) == "ravi"
    clock.t = 18
    assert s.get(sid) == "ravi"
    clock.t = 25
    assert s.get(sid) is None, "absolute=25 must be respected."


def test_destroy(store):
    sid = store.create("asha")
    other = store.create("ravi")
    store.destroy(sid)
    assert store.get(sid) is None, "After destroy() (logout) the id must not work."
    assert store.get(other) == "ravi", "destroy() must remove only that session."
    store.destroy(sid)
    store.destroy(None)
    store.destroy("never-existed")


def test_rotate_replaces_the_id(store):
    old = store.create("asha")
    new = store.rotate(old)
    assert isinstance(new, str) and new != old, "rotate() must return a NEW id."
    assert store.get(old) is None, "After rotate() the old id must be dead (session fixation, chapter 3.3)."
    assert store.get(new) == "asha", "The new id carries the same user."


def test_rotate_at_login_sets_the_user(store):
    planted = store.create("anonymous")          # the attacker knows this id
    sid = store.rotate(planted, user="asha")
    assert store.get(planted) is None, "The attacker's planted id must not become Asha's session."
    assert store.get(sid) == "asha", "rotate(old, user='asha') gives the new session to asha."


def test_rotate_unknown_or_expired_returns_none(store, clock):
    assert store.rotate("nope") is None, "rotate() of an unknown id returns None."
    assert store.rotate(None) is None, "rotate(None) returns None."
    old = store.create("asha")
    clock.t = 99999
    assert store.rotate(old) is None, "rotate() of an expired session returns None: you cannot refresh a dead session."
    assert store.get(old) is None
    assert "asha" not in repr(vars(store)), "No new session may be created from an expired one."


def test_rotate_does_not_extend_the_absolute_limit(store, clock):
    sid = store.create("asha")
    for t in range(1000, 20001, 1000):          # an active user: used every 1000 s
        clock.t = t
        assert store.get(sid) == "asha"
    new = store.rotate(sid)
    assert new is not None, "A live session can be rotated."
    for t in range(21000, 28800, 1000):
        clock.t = t
        assert store.get(new) == "asha", f"At t={t} the rotated session is active and younger than 8 h (counted from the FIRST create)."
    clock.t = 28799
    assert store.get(new) == "asha", "Just before 8 h after the ORIGINAL creation: alive."
    clock.t = 28800
    assert store.get(new) is None, "The rotated session inherits the creation time: it dies 8 h after the first create(), not after the rotate()."


def test_rotate_restarts_the_idle_timer(store, clock):
    sid = store.create("asha")
    clock.t = 1700
    new = store.rotate(sid)
    clock.t = 3499
    assert store.get(new) == "asha", "The new session counts as used at the moment of rotation (1799 s ago: alive)."
