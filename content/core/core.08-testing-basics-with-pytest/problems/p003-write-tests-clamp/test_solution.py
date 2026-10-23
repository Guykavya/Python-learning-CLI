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

CORRECT = 'def clamp(x, low, high):\n    """Return x limited to the range low..high (low <= high)."""\n    if x < low:\n        return low\n    if x > high:\n        return high\n    return x'

MUTANTS = {
    'no_low_check': ('def clamp(x, low, high):\n    if x > high:\n        return high\n    return x',
        'clamp(-5, 0, 10) returns -5 instead of 0 (values below the range are not raised to low).'),
    'no_high_check': ('def clamp(x, low, high):\n    if x < low:\n        return low\n    return x',
        'clamp(15, 0, 10) returns 15 instead of 10 (values above the range are not cut to high).'),
    'inside_returns_low': ('def clamp(x, low, high):\n    if x > high:\n        return high\n    return low',
        'values inside the range are replaced by low.'),
    'abs_bug': ('def clamp(x, low, high):\n    x = abs(x)\n    if x < low:\n        return low\n    if x > high:\n        return high\n    return x',
        'negative numbers are turned positive first, so clamp(-5, -10, -1) gives -1.'),
    'high_edge_wrong': ('def clamp(x, low, high):\n    if x < low:\n        return low\n    if x >= high:\n        return high - 1\n    return x',
        'x equal to high is treated as above the range, so clamp(10, 0, 10) gives 9.'),
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


def test_catches_no_low_check():
    caught('no_low_check')

def test_catches_no_high_check():
    caught('no_high_check')

def test_catches_inside_returns_low():
    caught('inside_returns_low')

def test_catches_abs_bug():
    caught('abs_bug')

def test_catches_high_edge_wrong():
    caught('high_edge_wrong')
