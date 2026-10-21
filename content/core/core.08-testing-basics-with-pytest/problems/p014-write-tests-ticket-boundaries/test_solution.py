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

CORRECT = 'def ticket_price(age):\n    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""\n    if age < 0:\n        raise ValueError("age cannot be negative")\n    if age < 5:\n        return 0\n    if age < 13:\n        return 50\n    if age < 60:\n        return 100\n    return 60'

MUTANTS = {
    'free_until_3': ('def ticket_price(age):\n    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""\n    if age < 0:\n        raise ValueError("age cannot be negative")\n    if age < 4:\n        return 0\n    if age < 13:\n        return 50\n    if age < 60:\n        return 100\n    return 60',
        'the free range stops one year early, so age 4 pays 50.'),
    'child_until_11': ('def ticket_price(age):\n    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""\n    if age < 0:\n        raise ValueError("age cannot be negative")\n    if age < 5:\n        return 0\n    if age < 12:\n        return 50\n    if age < 60:\n        return 100\n    return 60',
        'the child range stops one year early, so age 12 pays 100.'),
    'adult_until_60': ('def ticket_price(age):\n    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""\n    if age < 0:\n        raise ValueError("age cannot be negative")\n    if age < 5:\n        return 0\n    if age < 13:\n        return 50\n    if age <= 60:\n        return 100\n    return 60',
        'the adult range includes age 60, so a 60-year-old pays 100.'),
    'adult_ends_58': ('def ticket_price(age):\n    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""\n    if age < 0:\n        raise ValueError("age cannot be negative")\n    if age < 5:\n        return 0\n    if age < 13:\n        return 50\n    if age < 59:\n        return 100\n    return 60',
        'the adult range stops at 58, so a 59-year-old pays 60.'),
    'negative_allowed': ('def ticket_price(age):\n    """Ticket price by age: 0-4 free, 5-12 child (50), 13-59 adult (100), 60 and over senior (60)."""\n    if age < 5:\n        return 0\n    if age < 13:\n        return 50\n    if age < 60:\n        return 100\n    return 60',
        'a negative age is accepted (returns 0) instead of raising ValueError.'),
}

MIN_TESTS = 5


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


def test_catches_free_until_3():
    caught('free_until_3')

def test_catches_child_until_11():
    caught('child_until_11')

def test_catches_adult_until_60():
    caught('adult_until_60')

def test_catches_adult_ends_58():
    caught('adult_ends_58')

def test_catches_negative_allowed():
    caught('negative_allowed')


def test_requirement_1():
    assert 'raises' in LEARNER_SOURCE, 'Use pytest.raises(ValueError) for the negative age.'
