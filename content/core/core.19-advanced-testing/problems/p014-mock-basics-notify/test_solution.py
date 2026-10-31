import ast
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT target (all your tests must pass), then against several BUGGY
# targets (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

CORRECT = 'def notify(sender, user, message):\n    """Send message to the user through sender. Return True if sent, False if the message is blank."""\n    text = message.strip()\n    if not text:\n        return False\n    sender.send(user["email"], "[notice] " + text)\n    return True'

MUTANTS = {'wrong_address': ('def notify(sender, user, message):\n    text = message.strip()\n    if not text:\n        return False\n    sender.send(user["name"], "[notice] " + text)\n    return True', "the message is sent to user['name'] instead of user['email']."), 'no_prefix': ('def notify(sender, user, message):\n    text = message.strip()\n    if not text:\n        return False\n    sender.send(user["email"], text)\n    return True', "the '[notice] ' prefix is missing from the sent text."), 'blank_is_sent': ('def notify(sender, user, message):\n    text = message.strip()\n    sender.send(user["email"], "[notice] " + text)\n    return True', 'a blank message is sent anyway.'), 'no_strip': ('def notify(sender, user, message):\n    if not message.strip():\n        return False\n    sender.send(user["email"], "[notice] " + message)\n    return True', 'spaces around the message are not stripped before sending.'), 'sends_twice': ('def notify(sender, user, message):\n    text = message.strip()\n    if not text:\n        return False\n    sender.send(user["email"], "[notice] " + text)\n    sender.send(user["email"], "[notice] " + text)\n    return True', 'the message is sent twice.'), 'blank_returns_true': ('def notify(sender, user, message):\n    text = message.strip()\n    if not text:\n        return True\n    sender.send(user["email"], "[notice] " + text)\n    return True', 'a blank message returns True instead of False.'), 'returns_none': ('def notify(sender, user, message):\n    text = message.strip()\n    if not text:\n        return False\n    sender.send(user["email"], "[notice] " + text)', 'a sent message returns None instead of True.')}

MIN_TESTS = 4


@lru_cache(maxsize=None)
def run_suite(target_source):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short"],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop in a test?)"
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), ".")


def test_tests_pass_on_the_correct_code():
    code, out = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value or a wrong mock setup is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def caught(name):
    source, why = MUTANTS[name]
    code, out = run_suite(source)
    assert code == 1, (
        f"Your tests did NOT catch this bug: {why} "
        "Add a test whose expected value differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))


def test_catches_wrong_address():
    caught('wrong_address')

def test_catches_no_prefix():
    caught('no_prefix')

def test_catches_blank_is_sent():
    caught('blank_is_sent')

def test_catches_no_strip():
    caught('no_strip')

def test_catches_sends_twice():
    caught('sends_twice')

def test_catches_blank_returns_true():
    caught('blank_returns_true')

def test_catches_returns_none():
    caught('returns_none')


def test_requirement_mock_tools():
    for word in ("Mock", "assert_called_once_with", "assert_not_called"):
        assert word in LEARNER_SOURCE, f"Use {word} somewhere in your tests (see the problem text)."
