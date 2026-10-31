import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is copied into a temporary project as conftest.py
# (so its fixtures are visible), next to target.py (the code below) and a test file written by
# the checker. Those tests use your make_user fixture and look at the registry afterwards.

LEARNER_SOURCE = Path(__file__).with_name("solution.py").read_text()

TARGET = r'''_USERS = {}


def create_user(name, admin=False):
    if name in _USERS:
        raise ValueError(f"user {name!r} already exists")
    user = {"name": name, "admin": admin}
    _USERS[name] = user
    return user


def delete_user(name):
    del _USERS[name]


def all_users():
    return sorted(_USERS)'''

CHECK = """
from target import all_users, delete_user


def test_1_factory_creates_users(make_user):
    ann = make_user("ann")
    bob = make_user("bob", admin=True)
    assert ann == {"name": "ann", "admin": False}
    assert bob == {"name": "bob", "admin": True}
    assert all_users() == ["ann", "bob"]


def test_2_registry_is_empty_again(make_user):
    assert all_users() == []
    make_user("ann")


def test_3_default_arguments(make_user):
    assert make_user("zed")["admin"] is False


def test_4_user_deleted_by_the_test_itself(make_user):
    make_user("tmp")
    delete_user("tmp")
    assert all_users() == []


def test_5_teardown_survived_the_manual_delete(make_user):
    assert all_users() == []


def test_6_many_users(make_user):
    for i in range(5):
        make_user(f"u{i}")
    assert len(all_users()) == 5


def test_7_registry_is_empty_at_the_end():
    assert all_users() == []
"""


@lru_cache(maxsize=None)
def run_project():
    with tempfile.TemporaryDirectory(prefix="learn-fact-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(TARGET)
        (tmp / "conftest.py").write_text(LEARNER_SOURCE)
        (tmp / "test_check.py").write_text(CHECK)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_check.py", "-q", "--no-header", "-p", "no:cacheprovider",
                 "--tb=short", "--junitxml=report.xml"],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out", {}
        results = {}
        report = tmp / "report.xml"
        if report.exists():
            for tc in ET.parse(report).getroot().iter("testcase"):
                status = "passed"
                for child in tc:
                    if child.tag in ("failure", "error"):
                        status = "failed"
                        break
                results[tc.get("name")] = status
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), "."), results


def check(name, advice):
    code, out, results = run_project()
    assert results, "pytest collected nothing or crashed. pytest said:\n" + out[-900:]
    assert results.get(name) == "passed", f"{name} failed. {advice}\npytest said:\n" + out[-900:]


def test_factory_returns_a_function_that_creates_users():
    check("test_1_factory_creates_users",
          "make_user must RETURN a function make(name, admin=False) that calls create_user and returns the user dict.")


def test_default_admin_argument():
    check("test_3_default_arguments", "make(name, admin=False): admin must default to False.")


def test_users_are_deleted_after_each_test():
    check("test_2_registry_is_empty_again",
          "Users made in an earlier test are still in the registry. After the yield, delete every user the factory created "
          "(keep a list of the names you created).")


def test_all_created_users_are_deleted_not_only_the_last():
    check("test_6_many_users", "Delete ALL users the factory created, in a loop over your cleanup list.")
    check("test_7_registry_is_empty_at_the_end", "Some users survived the last factory test: clean up every one.")


def test_teardown_survives_a_user_the_test_already_deleted():
    check("test_4_user_deleted_by_the_test_itself",
          "The test deleted its user itself, so your teardown's delete_user raises KeyError and the test ERRORS. "
          "Only delete names that are still in all_users() (or catch KeyError).")
    check("test_5_teardown_survived_the_manual_delete", "The registry should be empty after the previous test.")
