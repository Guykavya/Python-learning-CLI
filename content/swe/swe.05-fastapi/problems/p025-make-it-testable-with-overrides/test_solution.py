from datetime import date

import pytest
from fastapi.testclient import TestClient

from solution import Settings, app, get_clock, get_settings


@pytest.fixture
def use():
    """use(day, grace) installs the overrides and returns a client."""
    clients = []

    def install(day, grace=0):
        app.dependency_overrides[get_clock] = lambda: day
        app.dependency_overrides[get_settings] = lambda: Settings(grace_days=grace)
        client = TestClient(app)
        clients.append(client)
        return client

    try:
        yield install
    finally:
        app.dependency_overrides.clear()


def test_status_uses_the_injected_clock(use):
    client = use(date(2020, 1, 15))
    assert client.get("/tasks/1/status").json() == {"id": 1, "title": "pay rent", "overdue": True, "days_left": -5}, (
        "On 2020-01-15 task 1 (due 2020-01-10) is 5 days late. If you got a big negative number, the endpoint "
        "still calls date.today() instead of using Depends(get_clock).")
    assert client.get("/tasks/2/status").json() == {"id": 2, "title": "file taxes", "overdue": False, "days_left": 5}, (
        "On 2020-01-15 task 2 (due 2020-01-20) has 5 days left and is not overdue.")


def test_overdue_list_uses_the_injected_clock(use):
    assert use(date(2020, 1, 15)).get("/overdue").json() == {"overdue": [1]}, "On 2020-01-15 only task 1 is overdue."
    assert use(date(2020, 3, 2)).get("/overdue").json() == {"overdue": [1, 2, 3]}, "On 2020-03-02 all three are overdue."
    assert use(date(2020, 1, 1)).get("/overdue").json() == {"overdue": []}, "On 2020-01-01 nothing is overdue."


def test_grace_comes_from_the_injected_settings(use):
    client = use(date(2020, 1, 15), grace=7)
    assert client.get("/overdue").json() == {"overdue": []}, (
        "With 7 days of grace task 1 is overdue only after 2020-01-17. If task 1 is still listed, the endpoint "
        "reads GRACE_DAYS from the environment instead of Depends(get_settings).")
    body = client.get("/tasks/1/status").json()
    assert body["overdue"] is False and body["days_left"] == -5, (
        f"Grace changes 'overdue' but not days_left (still due - today = -5); got {body}")


def test_last_day_of_grace_is_not_overdue(use):
    assert use(date(2020, 1, 17), grace=7).get("/tasks/1/status").json()["overdue"] is False, (
        "2020-01-17 is the last day of grace (due 01-10 + 7): not overdue yet. Use '>' not '>='.")
    assert use(date(2020, 1, 18), grace=7).get("/tasks/1/status").json()["overdue"] is True, "2020-01-18 is after the grace period."


def test_due_day_itself_is_not_overdue(use):
    body = use(date(2020, 1, 10)).get("/tasks/1/status").json()
    assert body["overdue"] is False and body["days_left"] == 0, f"On the due day itself: not overdue, 0 days left; got {body}"


def test_unknown_task_is_404(use):
    r = use(date(2020, 1, 15)).get("/tasks/9/status")
    assert r.status_code == 404 and r.json() == {"detail": "Task not found"}, f"Got {r.status_code} {r.text}"


def test_environment_does_not_leak_into_the_endpoints(use, monkeypatch):
    monkeypatch.setenv("GRACE_DAYS", "100")
    client = use(date(2020, 1, 15), grace=0)
    assert client.get("/overdue").json() == {"overdue": [1]}, (
        "GRACE_DAYS=100 is set in the environment, but the overridden settings say 0. The endpoint must use the "
        "injected settings only.")


def test_get_settings_reads_the_environment(monkeypatch):
    monkeypatch.delenv("GRACE_DAYS", raising=False)
    assert get_settings() == Settings(grace_days=0), "Without GRACE_DAYS the grace is 0."
    monkeypatch.setenv("GRACE_DAYS", "4")
    assert get_settings() == Settings(grace_days=4), "get_settings() must read GRACE_DAYS when it is called."


def test_get_clock_is_today():
    assert get_clock() == date.today(), "The real get_clock returns date.today()."
