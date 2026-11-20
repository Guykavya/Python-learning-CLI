import hashlib
import re

import pytest

from solution import ResetTokens


class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def tokens(clock):
    return ResetTokens(clock)


def test_token_shape(tokens):
    t = tokens.issue("asha")
    assert isinstance(t, str) and len(t) == 43, f"Use secrets.token_urlsafe(32): 43 characters; got {len(t) if isinstance(t, str) else t!r}"
    assert re.fullmatch(r"[A-Za-z0-9_-]+", t), "A url-safe token uses only letters, digits, '-' and '_'."


def test_tokens_are_unique(tokens):
    seen = {tokens.issue(f"user{i}") for i in range(200)}
    assert len(seen) == 200, "200 tokens must all be different: generate each one with secrets, never from a counter or the user name."


def test_valid_once(tokens):
    t = tokens.issue("asha")
    assert tokens.consume(t) == "asha", "A fresh token returns the user name."
    assert tokens.consume(t) is None, "A token works ONCE: the second consume must return None."


def test_expiry_boundary(tokens, clock):
    t = tokens.issue("asha")
    clock.t += 899
    assert tokens.consume(t) == "asha", "899 s after issue the token is still valid (ttl is 900)."
    t2 = tokens.issue("asha")
    clock.t += 900
    assert tokens.consume(t2) is None, "At exactly 900 s the token is expired: use `now >= expires`, not `>`."


def test_custom_ttl(clock):
    short = ResetTokens(clock, ttl=60)
    t = short.issue("ravi")
    clock.t += 61
    assert short.consume(t) is None, "ttl=60 must be respected."


def test_expired_token_is_gone_for_good(tokens, clock):
    t = tokens.issue("asha")
    clock.t += 5000
    assert tokens.consume(t) is None
    clock.t = 1000
    assert tokens.consume(t) is None, "An expired token must be removed when it is tried; it must not come back to life."


def test_new_token_cancels_the_old_one(tokens):
    first = tokens.issue("asha")
    second = tokens.issue("asha")
    assert tokens.consume(first) is None, "The first token must stop working when a new one is issued for the same user."
    assert tokens.consume(second) == "asha", "The newest token works."


def test_other_users_are_not_affected(tokens):
    a = tokens.issue("asha")
    r = tokens.issue("ravi")
    assert tokens.consume(r) == "ravi", "Ravi's token works."
    assert tokens.consume(a) == "asha", "Issuing a token for Ravi must not cancel Asha's."


def test_using_a_token_does_not_revive_the_old_ones(tokens):
    first = tokens.issue("asha")
    second = tokens.issue("asha")
    assert tokens.consume(second) == "asha"
    assert tokens.consume(first) is None, "The cancelled token stays cancelled after the newest one was used."
    assert tokens.consume(second) is None


@pytest.mark.parametrize("junk", ["", "abc", "A" * 43, " ", "../../etc/passwd", "x" * 10_000])
def test_junk_returns_none(tokens, junk):
    tokens.issue("asha")
    try:
        result = tokens.consume(junk)
    except Exception as exc:
        pytest.fail(f"consume({junk[:20]!r}) raised {type(exc).__name__}; unknown tokens return None.")
    assert result is None, f"consume of an unknown token must be None; got {result!r}"


def test_only_the_hash_is_stored(tokens):
    t = tokens.issue("asha")
    state = repr(vars(tokens))
    assert t not in state, "The token itself is stored on the object. Store only its SHA-256 hex digest (a stolen table must not contain working links)."
    digest = hashlib.sha256(t.encode()).hexdigest()
    assert digest in state, "Store hashlib.sha256(token.encode()).hexdigest() as the key (chapter 2.6)."


def test_issue_does_not_use_the_real_clock(tokens, clock):
    t = tokens.issue("asha")
    clock.t = 10**12
    assert tokens.consume(t) is None, "Expiry must follow the injected clock()."
