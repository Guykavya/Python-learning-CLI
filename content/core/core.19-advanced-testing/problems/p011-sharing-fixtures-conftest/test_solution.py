import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

import solution

# How this check works: your solution.py holds two strings, CONFTEST and API_CONFTEST. The
# checker builds a small project in a temporary folder:
#
#     tests/conftest.py        <- CONFTEST
#     tests/test_top.py        <- written by the checker
#     tests/api/conftest.py    <- API_CONFTEST
#     tests/api/test_api.py    <- written by the checker
#
# and runs real pytest on it. The test files never import anything from the conftest files:
# the fixtures are found by name, which is the whole point of conftest.py.

TEST_TOP = """
def test_config_default(app_config):
    assert app_config == {"debug": False, "db": "memory"}


def test_user_uses_config(user):
    assert user == {"name": "ada", "db": "memory"}


def test_mutate_config(app_config):
    app_config["debug"] = True


def test_config_is_fresh_again(app_config):
    assert app_config["debug"] is False
"""

TEST_API = """
def test_api_config(app_config):
    assert app_config == {"debug": True, "db": "api-db"}


def test_user_follows_the_override(user):
    assert user == {"name": "ada", "db": "api-db"}
"""


@lru_cache(maxsize=None)
def run_project():
    with tempfile.TemporaryDirectory(prefix="learn-conf-") as tmp:
        tmp = Path(tmp)
        (tmp / "tests" / "api").mkdir(parents=True)
        (tmp / "tests" / "conftest.py").write_text(solution.CONFTEST)
        (tmp / "tests" / "api" / "conftest.py").write_text(solution.API_CONFTEST)
        (tmp / "tests" / "test_top.py").write_text(TEST_TOP)
        (tmp / "tests" / "api" / "test_api.py").write_text(TEST_API)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "tests", "-q", "--no-header", "-p", "no:cacheprovider",
                 "--import-mode=importlib", "--tb=short", "--junitxml=report.xml"],
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
                    if child.tag == "skipped":
                        status = "skipped"
                results[tc.get("name")] = status
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), "."), results


def check(name, advice):
    code, out, results = run_project()
    assert results, ("pytest collected nothing or crashed. Is CONFTEST valid Python (import pytest!)? pytest said:\n"
                     + out[-900:])
    assert results.get(name) == "passed", f"{name} did not pass. {advice}\npytest said:\n" + out[-900:]


def test_strings_are_conftest_files_not_tests():
    for label in ("CONFTEST", "API_CONFTEST"):
        text = getattr(solution, label)
        assert isinstance(text, str) and text.strip(), f"{label} must be a non-empty string with the text of a conftest.py."
        assert "def test_" not in text, f"{label} should only hold fixtures and helpers, no tests."


def test_top_level_fixture_app_config():
    check("test_config_default", "tests/conftest.py must define the fixture app_config returning {'debug': False, 'db': 'memory'}.")


def test_fixture_that_depends_on_a_fixture():
    check("test_user_uses_config", "The fixture user takes app_config as a parameter and returns {'name': 'ada', 'db': app_config['db']}.")


def test_each_test_gets_a_fresh_config():
    check("test_config_is_fresh_again",
          "A test changed app_config['debug'] and a LATER test saw the change: the fixture must build a new dict on every call "
          "(function scope, and create the dict inside the function, not at module level).")


def test_folder_conftest_overrides_the_fixture():
    check("test_api_config", "tests/api/conftest.py must define app_config again, returning {'debug': True, 'db': 'api-db'}. "
          "A fixture in a deeper conftest overrides the one above it, only for tests in that folder.")


def test_the_dependent_fixture_picks_up_the_override():
    check("test_user_follows_the_override",
          "Do NOT redefine user in the api conftest. user asks for app_config by name, so inside tests/api it automatically "
          "receives the overridden one.")


def test_top_tests_still_see_the_original_config():
    check("test_config_default", "The override in tests/api must not affect tests outside that folder.")
    check("test_user_uses_config", "tests outside tests/api must still get db 'memory'.")


def test_api_conftest_does_not_copy_user():
    assert "def user" not in solution.API_CONFTEST, (
        "The api conftest should override only app_config; user must be inherited from the parent conftest.")
