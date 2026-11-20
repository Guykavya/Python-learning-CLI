import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict, Field

from solution import CASES


def make_app(min_title=1, max_title=100, min_priority=1, max_priority=5, forbid_extra=True):
    class TaskIn(BaseModel):
        model_config = ConfigDict(extra="forbid" if forbid_extra else "ignore")
        title: str = Field(min_length=min_title, max_length=max_title)
        priority: int = Field(default=3, ge=min_priority, le=max_priority)
        tags: list[str] = []

    app = FastAPI()

    @app.post("/tasks", status_code=201)
    def create_task(task: TaskIn):
        return {"id": 1, **task.model_dump()}

    return app


CORRECT = make_app()
MUTANTS = {
    "empty titles accepted (min_length removed)": make_app(min_title=0),
    "title limit off by one (101 characters accepted)": make_app(max_title=101),
    "priority upper limit off by one (6 accepted)": make_app(max_priority=6),
    "unknown fields silently ignored (extra='forbid' removed)": make_app(forbid_extra=False),
}


def statuses(app):
    with TestClient(app) as client:
        return [client.post("/tasks", json=payload).status_code for payload, _ in CASES]


def test_cases_have_the_right_shape():
    assert isinstance(CASES, list), "CASES must be a list of (payload, expected_status) tuples."
    assert len(CASES) <= 25, f"At most 25 cases, you have {len(CASES)}: pick boundary values instead of many random ones."
    for item in CASES:
        assert isinstance(item, tuple) and len(item) == 2, f"Each case is a (payload, status) tuple, got {item!r}"
        assert item[1] in (201, 422), f"Expected status must be 201 or 422, got {item[1]!r} in {item!r}"


def test_both_outcomes_are_present():
    expected = {status for _, status in CASES}
    assert 201 in expected, "Add at least one valid payload (201): otherwise an app that refuses everything passes your tests."
    assert 422 in expected, "Add at least one invalid payload (422)."


def test_every_case_matches_the_correct_app():
    got = statuses(CORRECT)
    wrong = [(payload, want, have) for (payload, want), have in zip(CASES, got) if want != have]
    assert not wrong, "These expectations are wrong for the CORRECT app (payload, you expected, it answered):\n" + "\n".join(
        f"  {str(p)[:70]}  expected {w}, got {h}" for p, w, h in wrong)


@pytest.mark.parametrize("name", list(MUTANTS))
def test_mutant_is_caught(name):
    got = statuses(MUTANTS[name])
    caught = [payload for (payload, want), have in zip(CASES, got) if want != have]
    assert caught, (
        f"Mutant survived: {name}. None of your cases behaves differently on it. "
        "Add the payload that sits exactly one step past the rule it loosened.")
