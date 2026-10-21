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

CORRECT = 'def median(numbers):\n    """Middle value of a non-empty list. For an even count, the mean of the two middle values."""\n    if not numbers:\n        raise ValueError("median of an empty list")\n    ordered = sorted(numbers)\n    mid = len(ordered) // 2\n    if len(ordered) % 2 == 1:\n        return ordered[mid]\n    return (ordered[mid - 1] + ordered[mid]) / 2'

MUTANTS = {
    'no_sorting': ('def median(numbers):\n    """Middle value of a non-empty list. For an even count, the mean of the two middle values."""\n    if not numbers:\n        raise ValueError("median of an empty list")\n    ordered = numbers\n    mid = len(ordered) // 2\n    if len(ordered) % 2 == 1:\n        return ordered[mid]\n    return (ordered[mid - 1] + ordered[mid]) / 2',
        'the list is not sorted first, so unsorted input gives a wrong answer.'),
    'even_takes_upper_middle': ('def median(numbers):\n    """Middle value of a non-empty list. For an even count, the mean of the two middle values."""\n    if not numbers:\n        raise ValueError("median of an empty list")\n    ordered = sorted(numbers)\n    mid = len(ordered) // 2\n    if len(ordered) % 2 == 1:\n        return ordered[mid]\n    return ordered[mid]',
        'for an even count it returns the upper middle value instead of the mean of the two.'),
    'whole_number_mean': ('def median(numbers):\n    """Middle value of a non-empty list. For an even count, the mean of the two middle values."""\n    if not numbers:\n        raise ValueError("median of an empty list")\n    ordered = sorted(numbers)\n    mid = len(ordered) // 2\n    if len(ordered) % 2 == 1:\n        return ordered[mid]\n    return (ordered[mid - 1] + ordered[mid]) // 2',
        'the mean of the two middle values uses // so 2.5 becomes 2.'),
    'empty_returns_none': ('def median(numbers):\n    """Middle value of a non-empty list. For an even count, the mean of the two middle values."""\n    if not numbers:\n        return None\n    ordered = sorted(numbers)\n    mid = len(ordered) // 2\n    if len(ordered) % 2 == 1:\n        return ordered[mid]\n    return (ordered[mid - 1] + ordered[mid]) / 2',
        'median([]) returns None instead of raising ValueError.'),
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


def test_catches_no_sorting():
    caught('no_sorting')

def test_catches_even_takes_upper_middle():
    caught('even_takes_upper_middle')

def test_catches_whole_number_mean():
    caught('whole_number_mean')

def test_catches_empty_returns_none():
    caught('empty_returns_none')


def _functions():
    return [n for n in ast.walk(ast.parse(LEARNER_SOURCE)) if isinstance(n, ast.FunctionDef)]


def test_no_assert_on_a_tuple():
    for node in ast.walk(ast.parse(LEARNER_SOURCE)):
        if isinstance(node, ast.Assert):
            assert not isinstance(node.test, ast.Tuple), (
                "assert (condition, 'message') puts the pair in parentheses: a non-empty tuple is always "
                "true, so the assert can never fail. Write assert condition, 'message'.")


def test_every_test_checks_something():
    for func in _functions():
        if func.name.startswith("test_"):
            checks = [n for n in ast.walk(func) if isinstance(n, (ast.Assert, ast.With))]
            assert checks, (
                f"{func.name} has no assert and no 'with pytest.raises'. A test that checks nothing can "
                "never fail, so it protects nothing.")


def test_no_misspelled_test_names():
    for func in _functions():
        low = func.name.lower()
        if ("test" in low or "tset" in low or "tets" in low) and not func.name.startswith("test_"):
            raise AssertionError(
                f"{func.name} looks like a test, but its name does not start with test_, so pytest "
                "silently skips it. Check the spelling.")


def test_raises_block_holds_one_call():
    for node in ast.walk(ast.parse(LEARNER_SOURCE)):
        if isinstance(node, ast.With) and "raises" in ast.unparse(node.items[0].context_expr):
            assert len(node.body) == 1, (
                "Put only the ONE call that should raise inside 'with pytest.raises'. Lines after the "
                "first raising line never run, and other lines can raise by mistake.")
