import ast
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT code (all your tests must pass), then against several BUGGY
# copies (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

MODULE = "target"
MIN_TESTS = 2
HYPOTHESIS = True

CORRECT = r'''def max_subarray_sum(nums):
    """Largest sum of a non-empty run of neighbouring numbers (Kadane's algorithm).

    max_subarray_sum([2, -5, 3, 4]) == 7. All numbers negative: the best run is the single
    largest number. An empty list raises ValueError.
    """
    if not nums:
        raise ValueError("nums must not be empty")
    best = current = nums[0]
    for x in nums[1:]:
        current = max(x, current + x)
        best = max(best, current)
    return best'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'all_negative_gives_zero': ('best = current = nums[0]',
                             'best = 0\n    current = nums[0]',
                             'the best sum starts at 0, so a list of only negative numbers returns 0 instead '
                             'of its largest number.'),
 'ignores_last_number': ('for x in nums[1:]:',
                         'for x in nums[1:-1]:',
                         'the loop stops one number early, so a big last number is never added.'),
 'restarts_too_late': ('current = max(x, current + x)',
                       'current = x if current < -1 else current + x',
                       'the run restarts only when the running sum is below -1, so a running sum of exactly '
                       '-1 is carried on and drags the result down.'),
 'ignores_first_number': ('best = current = nums[0]\n    for x in nums[1:]:',
                          'best = current = 0\n    for x in nums[1:]:',
                          'the first number is never counted.'),
 'empty_returns_zero': ('    if not nums:\n        raise ValueError("nums must not be empty")\n',
                        '    if not nums:\n        return 0\n',
                        'an empty list returns 0 instead of raising ValueError.'),
 'forgets_best': ('        best = max(best, current)\n    return best',
                  '        best = current\n    return best',
                  'the answer is the sum of the run that ENDS at the last number, not the best run '
                  'anywhere.')}

# Makes hypothesis deterministic and quiet inside the temporary folder, whatever you wrote.
CONFTEST = """
from hypothesis import settings
settings.register_profile("learn", settings(derandomize=True, database=None, max_examples=100, deadline=None))
settings.load_profile("learn")
"""


def mutate(name):
    old, new, _why = MUTANTS[name]
    assert CORRECT.count(old) == 1, f"author error: snippet of {name} is not unique"
    return CORRECT.replace(old, new)


@lru_cache(maxsize=None)
def run_suite(target_source):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / (MODULE + ".py")).write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        (tmp / "conftest.py").write_text(CONFTEST)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short"],
                cwd=tmp, capture_output=True, text=True, timeout=90, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop or a test that is far too slow?)"
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), ".")


def test_tests_pass_on_the_correct_code():
    code, out = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value or a wrong property is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    tree = ast.parse(LEARNER_SOURCE)
    names = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def test_hypothesis_is_deterministic():
    if not HYPOTHESIS:
        return
    assert "given" in LEARNER_SOURCE, "Use hypothesis: import given and strategies, then decorate with @given(...)."
    assert "derandomize=True" in LEARNER_SOURCE and "database=None" in LEARNER_SOURCE, (
        "Put @settings(derandomize=True, database=None, max_examples=100) above every @given test. "
        "Derandomize makes the run repeatable and database=None stops hypothesis writing a .hypothesis folder.")
    for number in re.findall(r"max_examples\s*=\s*(\d+)", LEARNER_SOURCE):
        assert int(number) <= 100, "Keep max_examples at 100 or less so the checker stays fast."


def caught(name):
    _old, _new, why = MUTANTS[name]
    code, out = run_suite(mutate(name))
    assert code == 1, (
        f"Your tests did NOT catch the bug '{name}': {why} "
        "Add a test whose result differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))

def test_catches_all_negative_gives_zero():
    caught('all_negative_gives_zero')

def test_catches_ignores_last_number():
    caught('ignores_last_number')

def test_catches_restarts_too_late():
    caught('restarts_too_late')

def test_catches_ignores_first_number():
    caught('ignores_first_number')

def test_catches_empty_returns_zero():
    caught('empty_returns_zero')

def test_catches_forgets_best():
    caught('forgets_best')
