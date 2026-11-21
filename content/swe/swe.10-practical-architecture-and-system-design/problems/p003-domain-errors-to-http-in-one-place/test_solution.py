import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from solution import DomainError, InvalidInput, NotFound, RuleViolation, domain_error_to_http, install


class ProjectGone(NotFound):
    """A project-specific refinement: still a 'not found'."""


@pytest.mark.parametrize("exc, status", [
    (NotFound("x"), 404), (InvalidInput("x"), 422), (RuleViolation("x"), 409), (DomainError("x"), 400),
])
def test_status_codes(exc, status):
    assert domain_error_to_http(exc) == (status, {"detail": "x"}), f"{type(exc).__name__} must give ({status}, {{'detail': 'x'}})"


def test_subclasses_follow_their_parent():
    assert domain_error_to_http(ProjectGone("gone")) == (404, {"detail": "gone"}), \
        "A subclass of NotFound must still be a 404: use isinstance, not an exact type lookup."


def test_the_detail_is_the_message():
    assert domain_error_to_http(RuleViolation("assignee already has 3 open tasks"))[1] == {"detail": "assignee already has 3 open tasks"}


@pytest.mark.parametrize("bug", [ValueError("a bug"), KeyError("k"), RuntimeError("boom")])
def test_other_exceptions_are_re_raised(bug):
    with pytest.raises(type(bug)) as info:
        domain_error_to_http(bug)
    assert info.value is bug, "Re-raise the very same exception object (raise exc): a bug must stay a bug."


@pytest.fixture
def client():
    app = FastAPI()
    install(app)

    @app.get("/missing")
    def missing():
        raise NotFound("project not found")

    @app.get("/bad")
    def bad():
        raise InvalidInput("title must have 1 to 120 characters")

    @app.get("/full")
    def full():
        raise RuleViolation("assignee already has 3 open tasks")

    @app.get("/gone")
    def gone():
        raise ProjectGone("this project was archived")

    @app.get("/other")
    def other():
        raise DomainError("some other rule")

    @app.get("/bug")
    def bug():
        raise RuntimeError("a real bug")

    app.state.test = True
    return TestClient(app, raise_server_exceptions=False)


@pytest.mark.parametrize("path, status, detail", [
    ("/missing", 404, "project not found"),
    ("/bad", 422, "title must have 1 to 120 characters"),
    ("/full", 409, "assignee already has 3 open tasks"),
    ("/gone", 404, "this project was archived"),
    ("/other", 400, "some other rule"),
])
def test_routes_are_translated_in_one_place(client, path, status, detail):
    r = client.get(path)
    assert (r.status_code, r.json()) == (status, {"detail": detail}), f"{path}: expected {status} {{'detail': {detail!r}}}; got {r.status_code} {r.text}"


def test_a_bug_is_still_a_500(client):
    assert client.get("/bug").status_code == 500, "Only domain errors are translated; a RuntimeError stays a 500."


def test_exactly_one_handler_is_registered_for_the_domain_errors():
    app = FastAPI()
    install(app)
    handlers = app.exception_handlers
    assert DomainError in handlers, "Register the handler for DomainError."
    for subclass in (NotFound, InvalidInput, RuleViolation):
        assert subclass not in handlers, f"Do not register a separate handler for {subclass.__name__}: one handler for DomainError does it all."
