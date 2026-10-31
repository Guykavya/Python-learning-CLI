import ast
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called target.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT target (all your tests must pass), then against several BUGGY
# targets (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()
TREE = ast.parse(LEARNER_SOURCE)
TESTS = [n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]


def arg_names(fn):
    return [a.arg for a in fn.args.args]


def parse_report(path):
    results = {}
    for tc in ET.parse(path).getroot().iter("testcase"):
        status = "passed"
        for child in tc:
            if child.tag in ("failure", "error"):
                status = "failed"
                break
            if child.tag == "skipped":
                status = "xfailed" if child.get("type") == "pytest.xfail" else "skipped"
        results[tc.get("name")] = status
    return results


@lru_cache(maxsize=None)
def run_suite(target_source, extra=()):
    with tempfile.TemporaryDirectory(prefix="learn-mut-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(target_source)
        (tmp / "test_learner.py").write_text(LEARNER_SOURCE)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "test_learner.py", "-q", "--no-header",
                 "-p", "no:cacheprovider", "--tb=short", "--junitxml=report.xml", *extra],
                cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
        except subprocess.TimeoutExpired:
            return 124, "pytest timed out (infinite loop in a test?)", {}
        report = tmp / "report.xml"
        results = parse_report(report) if report.exists() else {}
    return proc.returncode, (proc.stdout + proc.stderr).replace(str(tmp), "."), results

CORRECT = r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total:.2f}")'''

MUTANTS = {
    'not_sorted': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sales:
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total:.2f}")''',
        'lines are printed in the given order instead of sorted by name.'),
    'sorted_by_amount': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales, key=lambda s: s[1]):
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total:.2f}")''',
        'lines are sorted by amount instead of by name.'),
    'no_total': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total += amount''',
        'the TOTAL line is missing.'),
    'amount_not_rounded': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount}")
        total += amount
    print(f"TOTAL: {total:.2f}")''',
        'amounts are not formatted with two decimals (4.5 should print as 4.50).'),
    'total_not_rounded': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total}")''',
        'the total is not formatted with two decimals.'),
    'total_is_last_amount': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total = amount
    print(f"TOTAL: {total:.2f}")''',
        'TOTAL shows only the last amount instead of the sum.'),
    'empty_prints_nothing': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total:.2f}")''',
        "an empty list should print 'No sales'."),
    'total_goes_to_stderr': (r'''import sys


def print_report(sales):
    """sales is a list of (name, amount) pairs. Print a sorted report, then the total."""
    if not sales:
        print("No sales")
        return
    total = 0
    for name, amount in sorted(sales):
        print(f"{name}: {amount:.2f}")
        total += amount
    print(f"TOTAL: {total:.2f}", file=sys.stderr)''',
        'the TOTAL line goes to stderr instead of stdout (check captured.out).'),
}

MIN_TESTS = 5


def test_tests_pass_on_the_correct_code():
    code, out, _ = run_suite(CORRECT)
    assert code != 5, ("No tests were collected. Write functions whose names start with test_ "
                       "in solution.py.")
    assert code == 0, ("Your tests must PASS on the correct code, but they failed or crashed. "
                       "A wrong expected value in your test is the usual cause. pytest said:\n"
                       + out[-1800:])


def test_you_wrote_enough_tests():
    names = [n.name for n in TESTS]
    assert len(names) >= MIN_TESTS, (
        f"Write at least {MIN_TESTS} test functions (names starting with test_); you have {len(names)}.")
    assert len(names) == len(set(names)), (
        "Two test functions share a name. The second silently replaces the first, so only one runs.")


def caught(name):
    source, why = MUTANTS[name]
    code, out, _ = run_suite(source)
    assert code == 1, (
        f"Your tests did NOT catch this bug: {why} "
        "Add a test whose expected value differs between the correct code and the buggy one."
        + ("" if code == 0 else f" (pytest exit code {code}; output: {out[-300:]})"))

def test_the_tests_really_use_capsys():
    users = [n for n in TESTS if "capsys" in arg_names(n)]
    assert len(users) >= 4, (
        "Check printed output with the capsys fixture: take capsys as a parameter in at least four tests. Found " + str(len(users)) + " test(s) taking capsys as a parameter.")


def test_catches_not_sorted():
    caught('not_sorted')


def test_catches_sorted_by_amount():
    caught('sorted_by_amount')


def test_catches_no_total():
    caught('no_total')


def test_catches_amount_not_rounded():
    caught('amount_not_rounded')


def test_catches_total_not_rounded():
    caught('total_not_rounded')


def test_catches_total_is_last_amount():
    caught('total_is_last_amount')


def test_catches_empty_prints_nothing():
    caught('empty_prints_nothing')


def test_catches_total_goes_to_stderr():
    caught('total_goes_to_stderr')
