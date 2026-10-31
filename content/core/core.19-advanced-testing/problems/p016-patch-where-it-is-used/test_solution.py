import sys
import types
from unittest.mock import patch

import pytest

from solution import targets

SOURCES = {
    "clock": """
def now():
    raise RuntimeError("the real clock was used in a test")
""",
    "mailer": """
class Mailer:
    def send(self, to, text):
        raise RuntimeError("a real email was sent in a test")
""",
    "app_greet": """
from clock import now
def greeting():
    return "morning" if now() < 12 else "afternoon"
""",
    "app_stamp": """
import clock
def stamp():
    return "at " + str(clock.now())
""",
    "app_files": """
from os.path import exists
def has_config():
    return exists("/home/you/.config/app.toml")
""",
    "app_mail": """
from mailer import Mailer
def welcome(name):
    return Mailer().send(name, "welcome")
""",
}


@pytest.fixture(autouse=True)
def modules(monkeypatch):
    for name in ("clock", "mailer", "app_greet", "app_stamp", "app_files", "app_mail"):
        module = types.ModuleType(name)
        monkeypatch.setitem(sys.modules, name, module)
        exec(SOURCES[name], module.__dict__)


def test_targets_returns_four_strings():
    t = targets()
    assert isinstance(t, dict), "targets() must return a dict."
    assert set(t) == {"greeting", "stamp", "has_config", "welcome"}, (
        "The dict needs exactly the keys greeting, stamp, has_config, welcome.")
    assert all(isinstance(v, str) and "." in v for v in t.values()), (
        "Every value is a string like 'module.name'.")


def test_greeting_target_controls_the_clock():
    import app_greet
    target = targets()["greeting"]
    with patch(target, return_value=9):
        assert app_greet.greeting() == "morning", (
            "app_greet did 'from clock import now', so it uses its OWN name 'now'. "
            "Patch that name (module app_greet), not the module where now() is defined.")
    with patch(target, return_value=15):
        assert app_greet.greeting() == "afternoon"


def test_stamp_target_controls_the_clock():
    import app_stamp
    with patch(targets()["stamp"], return_value=7):
        assert app_stamp.stamp() == "at 7", (
            "app_stamp does 'import clock' and calls clock.now(), so the lookup happens in module clock.")


def test_has_config_target_controls_exists():
    import app_files
    target = targets()["has_config"]
    with patch(target, return_value=True):
        assert app_files.has_config() is True, (
            "app_files did 'from os.path import exists': patch the name exists inside app_files.")
    with patch(target, return_value=False):
        assert app_files.has_config() is False


def test_welcome_target_replaces_the_mailer():
    import app_mail
    with patch(targets()["welcome"]) as mailer_class:
        mailer_class.return_value.send.return_value = "queued"
        assert app_mail.welcome("Ann") == "queued", (
            "app_mail calls Mailer() from its own namespace: patch 'app_mail.Mailer'.")
        mailer_class.return_value.send.assert_called_once_with("Ann", "welcome")


def test_no_target_patches_everything_globally():
    t = targets()
    assert not t["has_config"].startswith(("os.", "posixpath.", "ntpath.", "genericpath.")), (
        "Do not patch os.path.exists globally; patch the name inside the module that uses it.")
