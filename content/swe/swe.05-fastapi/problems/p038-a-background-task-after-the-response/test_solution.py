import logging

import pytest
from fastapi.testclient import TestClient
from starlette.background import BackgroundTasks

import solution
from solution import app, get_outbox, send_welcome


class FakeOutbox:
    def __init__(self, fail=False):
        self.messages, self.fail = [], fail

    def send(self, to, subject, body):
        if self.fail:
            raise ConnectionError("mail server unreachable")
        self.messages.append({"to": to, "subject": subject, "body": body})


@pytest.fixture
def outbox():
    fake = FakeOutbox()
    app.dependency_overrides[get_outbox] = lambda: fake
    try:
        yield fake
    finally:
        app.dependency_overrides.clear()


def test_signup_answers_201(outbox):
    with TestClient(app) as client:
        r = client.post("/signup", json={"email": "asha@example.com"})
    assert r.status_code == 201, f"Signup must still answer 201, got {r.status_code}"
    assert r.json() == {"email": "asha@example.com", "welcome": "queued"}


def test_one_welcome_message_is_sent(outbox):
    with TestClient(app) as client:
        client.post("/signup", json={"email": "asha@example.com"})
    assert len(outbox.messages) == 1, (
        f"Expected exactly one message in the outbox after one signup, found {len(outbox.messages)}. "
        "Did you schedule send_welcome with background.add_task, and does send_welcome call outbox.send?")
    message = outbox.messages[0]
    assert message["to"] == "asha@example.com" and message["subject"] == "Welcome to TaskFlow", (
        f"Wrong message: {message}. Use to=email and subject='Welcome to TaskFlow'.")
    assert message["body"] == "Hi asha@example.com, thanks for signing up."


def test_the_email_is_scheduled_as_a_background_task(outbox, monkeypatch):
    scheduled = []
    original = BackgroundTasks.add_task

    def spy(self, func, *args, **kwargs):
        scheduled.append((func, args))
        return original(self, func, *args, **kwargs)

    monkeypatch.setattr(BackgroundTasks, "add_task", spy)
    with TestClient(app) as client:
        client.post("/signup", json={"email": "ben@example.com"})
    assert [func for func, args in scheduled] == [send_welcome], (
        "The endpoint must call background.add_task(send_welcome, outbox, email) once, "
        "not call send_welcome itself (then the user would wait for the mail server).")
    assert scheduled[0][1] == (outbox, "ben@example.com"), (
        f"add_task got the arguments {scheduled[0][1]!r}; pass the outbox from the dependency, then the email.")


def test_a_failing_mail_server_does_not_change_the_response(caplog):
    broken = FakeOutbox(fail=True)
    app.dependency_overrides[get_outbox] = lambda: broken
    try:
        with caplog.at_level(logging.ERROR, logger="signup"):
            with TestClient(app) as client:
                r = client.post("/signup", json={"email": "cara@example.com"})
    finally:
        app.dependency_overrides.clear()
    assert r.status_code == 201, "A mail failure happens after the response: the signup is still a 201."
    failures = [rec for rec in caplog.records if "welcome email to cara@example.com failed" in rec.getMessage()]
    assert failures, (
        "send_welcome must catch the exception and log it with "
        "logger.exception('welcome email to %s failed', email); nobody else will ever see the failure.")
    assert failures[0].exc_info is not None, "Use logger.exception (not logger.error) so the traceback is in the log."


def test_send_welcome_alone():
    fake = FakeOutbox()
    send_welcome(fake, "dina@example.com")
    assert fake.messages and fake.messages[0]["to"] == "dina@example.com", "send_welcome(outbox, email) must call outbox.send."
    send_welcome(FakeOutbox(fail=True), "x@example.com")          # must not raise


def test_the_real_outbox_is_the_default():
    before = len(solution.OUTBOX.messages)
    with TestClient(app) as client:
        client.post("/signup", json={"email": "eve@example.com"})
    assert len(solution.OUTBOX.messages) == before + 1, "Without an override, get_outbox() gives the real OUTBOX."
