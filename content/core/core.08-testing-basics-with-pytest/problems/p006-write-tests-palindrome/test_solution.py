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

CORRECT = 'def is_palindrome(text):\n    """True if text reads the same backwards, ignoring upper/lower case and spaces."""\n    cleaned = text.lower().replace(" ", "")\n    return cleaned == cleaned[::-1]'

MUTANTS = {
    'case_sensitive': ('def is_palindrome(text):\n    cleaned = text.replace(" ", "")\n    return cleaned == cleaned[::-1]',
        "upper and lower case are treated as different letters ('Level' is rejected)."),
    'spaces_kept': ('def is_palindrome(text):\n    cleaned = text.lower()\n    return cleaned == cleaned[::-1]',
        "spaces are not removed ('nurses run' is rejected)."),
    'only_the_ends': ('def is_palindrome(text):\n    cleaned = text.lower().replace(" ", "")\n    if not cleaned:\n        return True\n    return cleaned[0] == cleaned[-1]',
        "only the first and last letters are compared ('abca' is accepted)."),
    'short_is_true': ('def is_palindrome(text):\n    cleaned = text.lower().replace(" ", "")\n    if len(cleaned) <= 2:\n        return True\n    return cleaned == cleaned[::-1]',
        "any text of two letters or fewer is accepted ('ab' is accepted)."),
    'empty_is_false': ('def is_palindrome(text):\n    cleaned = text.lower().replace(" ", "")\n    if cleaned == "":\n        return False\n    return cleaned == cleaned[::-1]',
        'the empty string is rejected.'),
}

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


def test_catches_case_sensitive():
    caught('case_sensitive')

def test_catches_spaces_kept():
    caught('spaces_kept')

def test_catches_only_the_ends():
    caught('only_the_ends')

def test_catches_short_is_true():
    caught('short_is_true')

def test_catches_empty_is_false():
    caught('empty_is_false')
