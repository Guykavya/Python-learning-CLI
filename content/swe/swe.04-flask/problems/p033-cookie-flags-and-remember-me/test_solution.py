from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

import pytest

from solution import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True})


def session_cookie(response):
    headers = [h for h in response.headers.getlist("Set-Cookie") if h.startswith("session=")]
    assert headers, "The response must set the session cookie (Set-Cookie: session=...)."
    return headers[-1]


def attributes(cookie):
    return {part.split("=")[0].strip().lower(): (part.split("=", 1)[1] if "=" in part else True) for part in cookie.split(";")[1:]}


def login(client, remember):
    data = {"username": "asha"}
    if remember:
        data["remember"] = "on"
    return client.post("/login", data=data)


def test_flags_are_set(app):
    attrs = attributes(session_cookie(login(app.test_client(), remember=False)))
    assert "httponly" in attrs, "Add SESSION_COOKIE_HTTPONLY = True."
    assert "secure" in attrs, "Add SESSION_COOKIE_SECURE = True (the cookie must travel over HTTPS only)."
    assert attrs.get("samesite") == "Lax", f"Add SESSION_COOKIE_SAMESITE = 'Lax', got {attrs.get('samesite')!r}."


def test_without_remember_it_is_a_browser_session_cookie(app):
    attrs = attributes(session_cookie(login(app.test_client(), remember=False)))
    assert "expires" not in attrs and "max-age" not in attrs, "Without 'remember' the cookie must have no Expires/Max-Age: it vanishes when the browser closes."


def test_remember_me_lasts_14_days(app):
    attrs = attributes(session_cookie(login(app.test_client(), remember=True)))
    assert "expires" in attrs, "With remember=on the session must be permanent: session.permanent = True makes Flask set Expires."
    expires = parsedate_to_datetime(attrs["expires"])
    left = expires - datetime.now(timezone.utc)
    assert timedelta(days=13, hours=23) < left < timedelta(days=14, hours=1), f"The cookie must expire in about 14 days (PERMANENT_SESSION_LIFETIME), not in {left}."


def test_remember_must_be_exactly_on(app):
    for value in ("", "off", "no"):
        r = app.test_client().post("/login", data={"username": "asha", "remember": value})
        assert "expires" not in attributes(session_cookie(r)), f"remember={value!r} is not 'on': keep a session cookie."


def test_config_can_be_overridden_for_tests():
    app = create_app({"TESTING": True, "SESSION_COOKIE_SECURE": False})
    attrs = attributes(session_cookie(login(app.test_client(), remember=False)))
    assert "secure" not in attrs, "test_config must be applied AFTER the defaults so a test can turn Secure off."


def test_login_replaces_the_old_session(app):
    client = app.test_client()
    with client.session_transaction() as s:
        s["leftover"] = "x"
    login(client, remember=False)
    with client.session_transaction() as s:
        assert s["user"] == "asha" and "leftover" not in s, "Call session.clear() before setting the user."


def test_logout_deletes_the_cookie(app):
    client = app.test_client()
    login(client, remember=True)
    r = client.post("/logout")
    assert r.get_data(as_text=True) == "bye"
    cookie = session_cookie(r)
    attrs = attributes(cookie)
    gone = cookie.startswith("session=;") or attrs.get("max-age") == "0"
    assert gone, f"Logout must make the browser delete the cookie (an empty value and a past Expires), got: {cookie}"
    assert client.get_cookie("session") is None
