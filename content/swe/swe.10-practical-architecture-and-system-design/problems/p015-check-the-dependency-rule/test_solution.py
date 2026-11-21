import pytest

from solution import violations

LAYERS = {"errors": "domain", "domain": "domain", "services": "services", "dispatch": "services",
          "notifications": "infrastructure", "repo": "infrastructure", "uow": "infrastructure", "mailer": "infrastructure", "db": "infrastructure", "main": "web"}


def check(module, source):
    return violations({module: source}, LAYERS)


def test_clean_domain_and_services():
    assert check("domain", "from dataclasses import dataclass\nfrom .errors import InvalidInput, RuleViolation\n") == []
    assert check("services", "from datetime import datetime\nfrom .domain import Task, drain_events\nfrom .errors import NotFound\n") == [], \
        "Services may import the domain (an inner layer) and the standard library."


def test_the_chapters_quick_fix_is_caught():
    source = "import sqlite3\nfrom .repo import SqliteTaskRepo\nfrom .domain import Task\n"
    assert check("services", source) == [("services", "repo"), ("services", "sqlite3")], \
        "The chapter's demonstration: services must not import the infrastructure layer or sqlite3."


def test_the_domain_must_not_import_outward():
    got = check("domain", "from .services import create_task\nfrom .mailer import send_email\nimport fastapi\nfrom .errors import RuleViolation\n")
    assert got == [("domain", "fastapi"), ("domain", "mailer"), ("domain", "services")], f"Got {got}"


def test_the_web_layer_may_import_everything_inside_it():
    source = "from . import services, repo, uow\nfrom .notifications import HANDLERS\nfrom fastapi import FastAPI\nimport sqlite3\n"
    assert check("main", source) == [], "The composition root knows all the concrete pieces; fastapi and sqlite3 are not banned for the web layer."


def test_infrastructure_may_use_sqlite_and_the_domain_but_not_the_web():
    assert check("repo", "import sqlite3\nimport json\nfrom .domain import Task\nfrom .errors import NotFound\n") == []
    assert check("uow", "from .db import connect\nfrom .repo import SqliteRepos\n") == [], "Same layer: allowed."
    assert check("uow", "from .main import task_json\n") == [("uow", "main")], "Infrastructure must not import the web layer."


def test_services_may_not_import_the_web_layer_try_it_of_the_chapter():
    assert check("services", "from .main import task_json\n") == [("services", "main")], \
        "The chapter's 'Try it: draw the line': services importing main reverses the arrow."


@pytest.mark.parametrize("line, expected", [
    ("from taskboard.repo import SqliteTaskRepo", [("services", "repo")]),
    ("from taskboard import repo", [("services", "repo")]),
    ("import taskboard.repo", [("services", "repo")]),
    ("import taskboard.repo as r", [("services", "repo")]),
    ("from . import repo", [("services", "repo")]),
    ("from .repo import X", [("services", "repo")]),
    ("from . import domain, errors", []),
    ("from taskboard import domain, errors", []),
    ("import taskboard", []),
    ("from fastapi.responses import JSONResponse", [("services", "fastapi")]),
    ("import httpx.exceptions", [("services", "httpx")]),
    ("import json, os", []),
    ("from otherpackage.repo import X", []),
])
def test_every_way_of_writing_an_import(line, expected):
    assert check("services", line + "\n") == expected, f"{line!r} should give {expected}"


def test_imports_inside_functions_count():
    source = "def late():\n    from .repo import SqliteTaskRepo\n    import sqlite3\n    return SqliteTaskRepo(sqlite3.connect(':memory:'))\n"
    assert check("services", source) == [("services", "repo"), ("services", "sqlite3")], "A hidden import inside a function is still a dependency."


def test_unknown_project_modules_are_ignored():
    assert check("services", "from .helpers import something\nfrom . import utils\n") == [], "A module that is not in the layers table is not judged."


def test_the_result_is_sorted_and_unique():
    source = "import sqlite3\nimport sqlite3\nfrom .repo import A\nfrom .repo import B\nfrom .mailer import send\n"
    assert check("services", source) == [("services", "mailer"), ("services", "repo"), ("services", "sqlite3")]


def test_several_modules_at_once():
    sources = {"domain": "from .services import x\n", "services": "from .domain import Task\n", "main": "from . import services\n"}
    assert violations(sources, LAYERS) == [("domain", "services")]


def test_a_module_missing_from_the_table_is_an_error():
    with pytest.raises(ValueError):
        violations({"mystery": "import os\n"}, LAYERS)


def test_syntax_errors_are_not_hidden():
    with pytest.raises(SyntaxError):
        check("services", "def broken(:\n")


def test_the_real_shape_of_taskboard_is_clean():
    sources = {
        "errors": "class DomainError(Exception):\n    pass\n",
        "domain": "from dataclasses import dataclass, field\nfrom .errors import InvalidInput, RuleViolation\n",
        "services": "from datetime import datetime, timezone\nfrom .domain import Task, drain_events\nfrom .errors import NotFound\n",
        "dispatch": "import logging\nfrom datetime import datetime, timezone\n",
        "notifications": "from . import mailer\n",
        "repo": "import json\nfrom dataclasses import dataclass\nfrom .domain import Task\n",
        "uow": "from .db import connect\nfrom .repo import SqliteRepos\n",
        "mailer": "SENT = []\n",
        "db": "import sqlite3\nfrom .schema import SCHEMA\n",
        "main": "import os\nfrom fastapi import BackgroundTasks, FastAPI\nfrom . import services\nfrom .dispatch import dispatch_pending\nfrom .uow import SqliteUnitOfWork\n",
    }
    assert violations(sources, LAYERS) == [], "The chapter's finished Taskboard obeys the rule: your checker must not invent violations."
