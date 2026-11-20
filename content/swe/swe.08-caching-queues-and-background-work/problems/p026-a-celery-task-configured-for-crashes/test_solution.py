import pytest

import solution
from solution import ProviderTimeout, app, send_welcome_email


class FakeProvider:
    def __init__(self):
        self.outbox, self.by_key = [], {}

    def send(self, to, subject, body, idempotency_key=None):
        if idempotency_key in self.by_key:
            return self.by_key[idempotency_key]
        message_id = f"msg-{len(self.outbox) + 1}"
        self.outbox.append({"to": to, "subject": subject, "key": idempotency_key})
        self.by_key[idempotency_key] = message_id
        return message_id


@pytest.fixture
def provider(monkeypatch):
    fake = FakeProvider()
    monkeypatch.setattr(solution, "get_provider", lambda: fake)
    monkeypatch.setattr(app.conf, "task_always_eager", True)
    return fake


def test_app_settings():
    conf = app.conf
    assert conf.task_serializer == "json" and list(conf.accept_content) == ["json"], \
        "Serialise tasks as JSON only (task_serializer='json', accept_content=['json']): pickle runs code from the broker."
    assert conf.task_acks_late is True, "task_acks_late=True: ack after the work, so a killed worker's task is redelivered."
    assert conf.task_reject_on_worker_lost is True, "task_reject_on_worker_lost=True: requeue when the worker process dies."
    assert conf.worker_prefetch_multiplier == 1, "worker_prefetch_multiplier=1: a crashed worker holds at most one task."


def test_task_options():
    t = send_welcome_email
    assert t.acks_late is True, "The task itself: acks_late=True."
    assert t.reject_on_worker_lost is True, "The task itself: reject_on_worker_lost=True."
    assert tuple(t.autoretry_for) == (ProviderTimeout,), f"autoretry_for=(ProviderTimeout,): retry only the temporary error; got {t.autoretry_for}"
    assert t.max_retries == 5, f"max_retries=5; got {t.max_retries}"
    assert t.retry_backoff is True and t.retry_jitter is True, "retry_backoff=True and retry_jitter=True: exponential delays with jitter."


def test_bound_task():
    assert send_welcome_email.name.endswith("send_welcome_email")
    import inspect
    params = list(inspect.signature(send_welcome_email.run).parameters)
    assert params == ["user_id", "to"], f"Declare the task with bind=True and the signature (self, user_id, to); run() shows {params}"


def test_eager_run_sends_with_key(provider):
    result = send_welcome_email.delay(7, "ada@example.com")
    assert result.get() == "msg-1", "The task returns the provider's message id."
    assert provider.outbox == [{"to": "ada@example.com", "subject": "Welcome!", "key": "welcome:7"}], \
        f"Send to the address with subject 'Welcome!' and idempotency_key='welcome:<user_id>'; got {provider.outbox}"


def test_running_twice_sends_once(provider):
    first = send_welcome_email.delay(7, "ada@example.com").get()
    second = send_welcome_email.delay(7, "ada@example.com").get()
    assert first == second and len(provider.outbox) == 1, \
        "With acks_late a task can run twice; the idempotency key must make the second run send nothing."


def test_provider_comes_from_get_provider(monkeypatch):
    monkeypatch.setattr(app.conf, "task_always_eager", True)
    called = []

    class P(FakeProvider):
        def send(self, *a, **kw):
            called.append(kw.get("idempotency_key"))
            return "x"

    monkeypatch.setattr(solution, "get_provider", lambda: P())
    send_welcome_email.delay(3, "bo@example.com").get()
    assert called == ["welcome:3"], "Look the provider up with get_provider() inside the task (the tests replace it)."
