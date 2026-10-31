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
MIN_TESTS = 4
HYPOTHESIS = True

CORRECT = r'''def reverse(items):
    """Return a new list with the items in reverse order. The input is not changed."""
    return list(items[::-1])


def sorted_copy(items):
    """Return a new list with the same numbers in ascending order. The input is not changed."""
    return sorted(items)'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'reverse_is_identity': ('return list(items[::-1])',
                         'return list(items)',
                         'reverse returns the list unchanged. Reversing twice still gives the original, so a '
                         'round-trip property alone cannot see it.'),
 'reverse_drops_last': ('return list(items[::-1])',
                        'return list(items[::-1][:-1])',
                        'reverse loses one element, so the result is shorter than the input.'),
 'sort_drops_duplicates': ('return sorted(items)',
                           'return sorted(set(items))',
                           'sorted_copy removes repeated numbers, so the result is shorter than the input.'),
 'sort_in_place': ('return sorted(items)',
                   'items.sort()\n    return items',
                   "sorted_copy sorts the caller's list in place instead of returning a new list."),
 'sort_by_absolute_value': ('return sorted(items)',
                            'return sorted(items, key=abs)',
                            'negative numbers are ordered by their absolute value, so the result is not '
                            'ascending.'),
 'sort_changes_values': ('return sorted(items)',
                         'return sorted(abs(x) for x in items)',
                         'the result is ascending and has the right length, but negative numbers were '
                         'replaced by positive ones.')}

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

def test_catches_reverse_is_identity():
    caught('reverse_is_identity')

def test_catches_reverse_drops_last():
    caught('reverse_drops_last')

def test_catches_sort_drops_duplicates():
    caught('sort_drops_duplicates')

def test_catches_sort_in_place():
    caught('sort_in_place')

def test_catches_sort_by_absolute_value():
    caught('sort_by_absolute_value')

def test_catches_sort_changes_values():
    caught('sort_changes_values')
