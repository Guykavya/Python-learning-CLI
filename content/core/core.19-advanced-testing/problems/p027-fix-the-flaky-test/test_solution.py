import ast
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests for target.py. It is run
# many times against the CORRECT target, each time with a different shuffled test order, a
# different PYTHONHASHSEED (this changes the order of sets) and a different "current hour".
# A well-written suite passes every time. Then it is run against buggy copies of target.py and
# must fail on each (so deleting the tests is not a fix).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

CORRECT = 'import random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()'

MUTANTS = {'noon_is_morning': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 13:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', "12:00 is greeted 'Good morning' instead of 'Good afternoon'."), 'evening_starts_late': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 19:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', "18:00 is greeted 'Good afternoon' instead of 'Good evening'."), 'afternoon_skipped': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n        return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', "the afternoon greeting is gone (12:00 to 17:59 say 'Good evening')."), 'tags_not_unique': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(tags)\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', 'duplicate tags are kept.'), 'tags_lose_one': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags[:-1]))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', 'the last tag is dropped.'), 'dice_from_zero': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(0, 5) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', 'dice can show 0 and never 6.'), 'dice_no_six': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 5) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', 'dice never show a 6.'), 'record_off_by_one': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events) - 1\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', 'record returns one less than the number of events.'), 'events_reversed': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(reversed(_events))\n\n\ndef clear():\n    """Forget all events."""\n    _events.clear()\n', 'events() returns the newest event first.'), 'clear_does_nothing': ('\nimport random\nfrom datetime import datetime\n\n_events = []\n\n\ndef current_hour():\n    return datetime.now().hour\n\n\ndef greeting():\n    """\'Good morning\' before 12:00, \'Good afternoon\' from 12:00 to 17:59, otherwise \'Good evening\'."""\n    hour = current_hour()\n    if hour < 12:\n        return "Good morning"\n    if hour < 18:\n        return "Good afternoon"\n    return "Good evening"\n\n\ndef unique_tags(tags):\n    """Return the distinct tags as a list. The order of the result is not specified."""\n    return list(set(tags))\n\n\ndef roll_dice(count, rng=None):\n    """Roll `count` six-sided dice. rng is an optional random.Random (default: the random module)."""\n    rng = rng or random\n    return [rng.randint(1, 6) for _ in range(count)]\n\n\ndef record(event):\n    """Remember an event and return how many events are stored now."""\n    _events.append(event)\n    return len(_events)\n\n\ndef events():\n    """Return a copy of the stored events, oldest first."""\n    return list(_events)\n\n\ndef clear():\n    """Forget all events."""\n    pass\n', 'clear() forgets nothing.')}

HOURS = [0, 4, 8, 11, 12, 14, 17, 18, 21, 23, 6, 15]
MIN_TESTS = 5

PLUGIN = """
import os
import random

import pytest

import target


def pytest_collection_modifyitems(items):
    random.Random(int(os.environ["FLAKY_SEED"])).shuffle(items)


@pytest.fixture(autouse=True)
def _pretend_hour(monkeypatch):
    monkeypatch.setattr(target, "current_hour", lambda: int(os.environ["FLAKY_HOUR"]))
"""


@lru_cache(maxsize=None)
def run_suite(target_source, seed):
    with tempfile.TemporaryDirectory(prefix="learn-flaky-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "flaky_plugin.py").write_text(PLUGIN)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1",
                   PYTHONHASHSEED=str(seed * 7 + 1), FLAKY_SEED=str(seed),
                   FLAKY_HOUR=str(HOURS[seed % len(HOURS)]))
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "-p", "flaky_plugin", "--tb=short"],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out"
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), ".")


def test_enough_tests_and_none_skipped():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, (
        f"Keep at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}. "
        "Fix the flaky tests, do not delete them.")
    assert len(names) == len(set(names)), "Two test functions share a name; one of them never runs."
    for word in ("skip", "xfail", "sleep", "importorskip"):
        assert word not in LEARNER_SOURCE, f"Do not use {word!r}: that hides flakiness, it does not fix it."


def test_passes_with_normal_run_of_the_correct_code():
    code, out = run_suite(CORRECT, 0)
    assert code != 5, "No tests were collected."
    assert code == 0, "Your tests fail on the correct code in the first (shuffled) run. pytest said:\n" + out[-1800:]


def test_passes_every_time_whatever_the_order_hash_seed_and_hour():
    for seed in range(1, len(HOURS)):
        code, out = run_suite(CORRECT, seed)
        assert code == 0, (
            f"Run {seed} of {len(HOURS)} failed: the suite is still flaky. In each run the test order is "
            "shuffled, PYTHONHASHSEED changes (order of sets/dicts of strings), the pretend 'current hour' "
            "changes, and unseeded random numbers differ. Which of those does the failing test depend on?\n"
            + out[-1800:])


def caught(name):
    source, why = MUTANTS[name]
    code, out = run_suite(source, 3)
    assert code == 1, (
        f"Your fixed tests no longer catch this bug: {why} A fix must keep every real check. "
        + ("" if code == 0 else f"(pytest exit code {code}: {out[-300:]})"))


def test_catches_noon_is_morning():
    caught('noon_is_morning')

def test_catches_evening_starts_late():
    caught('evening_starts_late')

def test_catches_afternoon_skipped():
    caught('afternoon_skipped')

def test_catches_tags_not_unique():
    caught('tags_not_unique')

def test_catches_tags_lose_one():
    caught('tags_lose_one')

def test_catches_dice_from_zero():
    caught('dice_from_zero')

def test_catches_dice_no_six():
    caught('dice_no_six')

def test_catches_record_off_by_one():
    caught('record_off_by_one')

def test_catches_events_reversed():
    caught('events_reversed')

def test_catches_clear_does_nothing():
    caught('clear_does_nothing')
