import pytest

from solution import DUMMY_HASH, LoginFailed, login

USERS = {"asha": "hash:asha-pass", "ravi": "hash:ravi-pass"}


class Verifier:
    """A fake checker that records every call. The dummy hash 'accepts' the password 'dummy'."""

    def __init__(self):
        self.calls = []

    def __call__(self, password, stored):
        self.calls.append((password, stored))
        if stored == DUMMY_HASH:
            return password == "dummy"
        return stored == "hash:" + password


def message_of(username, password):
    v = Verifier()
    with pytest.raises(LoginFailed) as info:
        login(USERS, username, password, v)
    return str(info.value), v


def test_success_returns_the_username_and_verifies_once():
    v = Verifier()
    assert login(USERS, "asha", "asha-pass", v) == "asha", "A correct login returns the username."
    assert v.calls == [("asha-pass", "hash:asha-pass")], f"verify must be called once, with the user's own stored hash; calls: {v.calls}"


def test_wrong_password_fails_with_the_generic_message():
    msg, v = message_of("asha", "wrong")
    assert msg == "invalid username or password", f"The message for a wrong password must be exactly 'invalid username or password'; got {msg!r}"
    assert len(v.calls) == 1, "verify must be called once."


def test_unknown_user_gets_the_same_message():
    wrong_pw, _ = message_of("asha", "wrong")
    unknown, _ = message_of("nobody", "anything")
    assert unknown == wrong_pw, "An unknown user and a wrong password must give the SAME message, or the message reveals which usernames exist."


def test_unknown_user_still_costs_one_verification_with_the_dummy():
    msg, v = message_of("nobody", "anything")
    assert len(v.calls) == 1, \
        f"verify was called {len(v.calls)} times for an unknown user; call it exactly once, with DUMMY_HASH, so the time looks the same (chapter 2.5)."
    assert v.calls[0] == ("anything", DUMMY_HASH), f"For an unknown user call verify(password, DUMMY_HASH); got {v.calls[0]}"


def test_known_user_does_not_touch_the_dummy():
    _, v = message_of("ravi", "nope")
    assert v.calls == [("nope", "hash:ravi-pass")], "A known user is checked against their own hash, not the dummy."


def test_unknown_user_cannot_log_in_even_if_the_dummy_verifies():
    v = Verifier()
    with pytest.raises(LoginFailed):
        login(USERS, "nobody", "dummy", v)         # verify(dummy password, DUMMY_HASH) is True here
    assert v.calls, "verify must still have been called."


def test_every_failure_is_the_same_class():
    for name, pw in (("asha", "x"), ("nobody", "x"), ("", ""), ("ASHA", "asha-pass")):
        v = Verifier()
        with pytest.raises(LoginFailed):
            login(USERS, name, pw, v)
        assert len(v.calls) == 1, f"login({name!r}, {pw!r}): exactly one verify call per attempt, got {len(v.calls)}"


def test_usernames_are_exact():
    v = Verifier()
    with pytest.raises(LoginFailed):
        login(USERS, "Asha", "asha-pass", v)
    assert v.calls[0][1] == DUMMY_HASH, "'Asha' is not in the table: treat it as an unknown user (use the dummy hash)."
