import ast
from datetime import datetime, timedelta
from pathlib import Path

import pytest

import solution
from solution import (
    ConsoleMailer,
    FixedClock,
    InMemoryMailer,
    InMemoryUserRepo,
    SignupError,
    SignupService,
    SystemClock,
    User,
    build_app,
)

MOMENT = datetime(2025, 3, 14, 9, 26)


class Spy:
    """One shared call log so the ORDER of calls can be checked."""

    def __init__(self):
        self.log = []


class FakeRepo:
    def __init__(self, spy):
        self.spy, self.users = spy, {}

    def exists(self, email):
        self.spy.log.append(("exists", email))
        return email in self.users

    def add(self, user):
        self.spy.log.append(("add", user.email))
        self.users[user.email] = user


class FakeMailer:
    def __init__(self, spy):
        self.spy, self.sent = spy, []

    def send(self, to, subject, body):
        self.spy.log.append(("send", to))
        self.sent.append((to, subject, body))


class FakeClock:
    def now(self):
        return MOMENT


def make_service():
    spy = Spy()
    repo, mailer = FakeRepo(spy), FakeMailer(spy)
    return SignupService(repo, mailer, FakeClock()), repo, mailer, spy


def test_signup_uses_only_the_injected_collaborators():
    service, repo, mailer, spy = make_service()
    user = service.signup("ana@example.com", "Ana")
    assert isinstance(user, User), "signup must return a User."
    assert (user.email, user.name, user.created_at) == ("ana@example.com", "Ana", MOMENT), (
        f"User fields wrong: {user}. created_at must come from clock.now(), not datetime.now()."
    )
    assert repo.users == {"ana@example.com": user}, "The user must be stored with repo.add(user)."
    assert len(mailer.sent) == 1 and mailer.sent[0][0] == "ana@example.com", "Exactly one welcome mail to the new user."
    assert "Ana" in mailer.sent[0][1], f"The subject {mailer.sent[0][1]!r} should greet the user by name."


def test_order_of_calls():
    service, _, _, spy = make_service()
    service.signup("ana@example.com", "Ana")
    assert spy.log == [("exists", "ana@example.com"), ("add", "ana@example.com"), ("send", "ana@example.com")], (
        f"Calls were {spy.log}. Check for a duplicate first, then save, then send the mail."
    )


def test_email_is_normalised():
    service, repo, mailer, _ = make_service()
    user = service.signup("  Ana@Example.COM ", "Ana")
    assert user.email == "ana@example.com", f"Emails are stripped and lower-cased, got {user.email!r}."


@pytest.mark.parametrize("bad", ["nope", "a@b", "@b.co", "a@@b.co", "", "a@b@c.co"])
def test_invalid_email_changes_nothing(bad):
    service, repo, mailer, spy = make_service()
    with pytest.raises(SignupError, match="invalid email"):
        service.signup(bad, "X")
    assert spy.log == [], f"Nothing may be called for an invalid email {bad!r}: validate first."


def test_duplicate_is_rejected_without_mail():
    service, repo, mailer, _ = make_service()
    service.signup("ana@example.com", "Ana")
    with pytest.raises(SignupError, match="already registered"):
        service.signup("ANA@example.com", "Ana again")
    assert len(mailer.sent) == 1 and len(repo.users) == 1, "A duplicate sends no second mail and stores nothing."


def test_signup_error_is_a_value_error():
    assert issubclass(SignupError, ValueError), "SignupError must subclass ValueError."


def test_build_app_test_environment_wires_fakes():
    app = build_app({"env": "test", "now": MOMENT})
    assert isinstance(app, SignupService), "build_app returns the wired SignupService."
    assert isinstance(app.repo, InMemoryUserRepo) and isinstance(app.mailer, InMemoryMailer), (
        "In the test environment use InMemoryUserRepo and InMemoryMailer."
    )
    assert isinstance(app.clock, FixedClock), "In the test environment use a FixedClock."
    user = app.signup("bo@example.com", "Bo")
    assert user.created_at == MOMENT, "The FixedClock must use config['now']."
    assert app.mailer.sent[0][0] == "bo@example.com", "InMemoryMailer.sent records (to, subject, body) tuples."
    assert app.repo.exists("bo@example.com") and app.repo.get("bo@example.com") == user, "Repo stores and returns the user."


def test_build_app_test_default_time_is_fixed():
    app = build_app({"env": "test"})
    a = app.signup("a@x.io", "A").created_at
    b = app.signup("b@x.io", "B").created_at
    assert a == b, "A FixedClock gives the same moment every time, even without config['now']."


def test_build_app_production_wiring(capsys):
    app = build_app({"env": "prod"})
    assert isinstance(app.clock, SystemClock) and isinstance(app.mailer, ConsoleMailer), (
        "Any env other than 'test' wires SystemClock and ConsoleMailer."
    )
    before = datetime.now()
    user = app.signup("cy@example.com", "Cy")
    assert before - timedelta(seconds=1) <= user.created_at <= datetime.now() + timedelta(seconds=1), (
        "SystemClock.now() must return the real current time."
    )
    out = capsys.readouterr().out
    assert out == "MAIL to=cy@example.com subject=Welcome, Cy\n", f"ConsoleMailer printed {out!r}."


def test_two_apps_do_not_share_users():
    one, two = build_app({"env": "test"}), build_app({"env": "test"})
    one.signup("ana@example.com", "Ana")
    two.signup("ana@example.com", "Ana")
    assert one.repo is not two.repo, (
        "Each build_app call must create its own repository. A module-level list or default argument would be shared."
    )


def _module_tree():
    return ast.parse(Path(solution.__file__).read_text())


def test_service_does_not_construct_concrete_classes():
    tree = _module_tree()
    classes = {n.name for n in tree.body if isinstance(n, ast.ClassDef)} - {"SignupService", "User", "SignupError"}
    service = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "SignupService")
    for node in ast.walk(service):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in classes | {"print"}:
            raise AssertionError(
                f"SignupService calls {node.func.id}(...). It must not create or use concrete collaborators: "
                "take repo, mailer and clock in __init__ and only call their methods."
            )
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise AssertionError("SignupService must not import anything inside its methods.")
        if isinstance(node, ast.Attribute) and node.attr == "now" and isinstance(node.value, ast.Name) and node.value.id == "datetime":
            raise AssertionError("SignupService must not call datetime.now(); use self.clock.now().")


def test_no_module_level_mutable_state():
    tree = _module_tree()
    for node in tree.body:
        if isinstance(node, ast.Assign):
            value = node.value
            mutable = isinstance(value, (ast.List, ast.Dict, ast.Set, ast.ListComp, ast.DictComp, ast.SetComp)) or (
                isinstance(value, ast.Call) and isinstance(value.func, ast.Name) and value.func.id in {"list", "dict", "set"}
            )
            assert not mutable, (
                f"Module-level mutable object on line {node.lineno}. Global lists and dicts are shared by every service "
                "and make tests depend on each other. Create the state inside the repo class."
            )
        assert not isinstance(node, ast.Global), "Do not use 'global'."
