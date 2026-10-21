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

CORRECT = 'def average(numbers):\n    """Return the mean of a non-empty list of numbers. Raise ValueError if it is empty."""\n    if not numbers:\n        raise ValueError("cannot average an empty list")\n    return sum(numbers) / len(numbers)'

MUTANTS = {
    'empty_returns_zero': ('def average(numbers):\n    """Return the mean of a non-empty list of numbers. Raise ValueError if it is empty."""\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)',
        'average([]) returns 0 instead of raising ValueError.'),
    'empty_zero_division': ('def average(numbers):\n    return sum(numbers) / len(numbers)',
        'average([]) leaks a ZeroDivisionError instead of raising ValueError.'),
    'wrong_message': ('def average(numbers):\n    """Return the mean of a non-empty list of numbers. Raise ValueError if it is empty."""\n    if not numbers:\n        raise ValueError("bad input")\n    return sum(numbers) / len(numbers)',
        "the ValueError message does not mention 'empty'."),
    'integer_division': ('def average(numbers):\n    """Return the mean of a non-empty list of numbers. Raise ValueError if it is empty."""\n    if not numbers:\n        raise ValueError("cannot average an empty list")\n    return sum(numbers) // len(numbers)',
        '// is used, so average([1, 2]) gives 1 instead of 1.5.'),
    'skips_last': ('def average(numbers):\n    """Return the mean of a non-empty list of numbers. Raise ValueError if it is empty."""\n    if not numbers:\n        raise ValueError("cannot average an empty list")\n    return sum(numbers[:-1]) / len(numbers)',
        'the last number is left out of the sum.'),
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


def test_catches_empty_returns_zero():
    caught('empty_returns_zero')

def test_catches_empty_zero_division():
    caught('empty_zero_division')

def test_catches_wrong_message():
    caught('wrong_message')

def test_catches_integer_division():
    caught('integer_division')

def test_catches_skips_last():
    caught('skips_last')


def test_requirement_1():
    assert 'raises' in LEARNER_SOURCE, 'Use pytest.raises(ValueError, match=...) for the empty list.'


def test_requirement_2():
    assert 'match' in LEARNER_SOURCE, 'Use match= so that the message is checked too.'
