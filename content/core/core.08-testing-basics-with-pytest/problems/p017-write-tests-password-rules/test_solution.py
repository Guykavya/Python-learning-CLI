import ast
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the function under test, and real pytest runs on it.
# First against the CORRECT target (all your tests must pass), then against several BUGGY
# targets (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

CORRECT = 'def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 8:\n        return False\n    if " " in pw:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_digit and has_lower and has_upper'

MUTANTS = {
    'min_length_7': ('def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 7:\n        return False\n    if " " in pw:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_digit and has_lower and has_upper',
        'a 7-character password is accepted (the minimum is 8).'),
    'min_length_9': ('def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 9:\n        return False\n    if " " in pw:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_digit and has_lower and has_upper',
        'an 8-character password is rejected (8 is allowed).'),
    'spaces_allowed': ('def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 8:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_digit and has_lower and has_upper',
        'a password containing a space is accepted.'),
    'no_digit_rule': ('def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 8:\n        return False\n    if " " in pw:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_lower and has_upper',
        'a password without a digit is accepted.'),
    'no_lower_rule': ('def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 8:\n        return False\n    if " " in pw:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_digit and has_upper',
        'a password without a lower-case letter is accepted.'),
    'no_upper_rule': ('def is_valid_password(pw):\n    """Valid: at least 8 characters, no spaces, and at least one digit, one lower and one upper letter."""\n    if len(pw) < 8:\n        return False\n    if " " in pw:\n        return False\n    has_digit = False\n    has_lower = False\n    has_upper = False\n    for ch in pw:\n        if ch.isdigit():\n            has_digit = True\n        if ch.islower():\n            has_lower = True\n        if ch.isupper():\n            has_upper = True\n    return has_digit and has_lower',
        'a password without an upper-case letter is accepted.'),
}

MIN_TESTS = 6


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


def test_tests_pass_on_the_correct_function():
    code, out = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct function, but they failed or crashed. "
                       "A wrong expected value in your test is the usual cause. pytest said:\n"
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
        "Add a test whose expected value differs between the correct function and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))


def test_catches_min_length_7():
    caught('min_length_7')

def test_catches_min_length_9():
    caught('min_length_9')

def test_catches_spaces_allowed():
    caught('spaces_allowed')

def test_catches_no_digit_rule():
    caught('no_digit_rule')

def test_catches_no_lower_rule():
    caught('no_lower_rule')

def test_catches_no_upper_rule():
    caught('no_upper_rule')
