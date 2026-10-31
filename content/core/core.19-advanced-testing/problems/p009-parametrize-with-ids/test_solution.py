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

CORRECT = r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"'''

MUTANTS = {
    'degenerate_is_valid': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b < c or a + c < b or b + c < a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"''',
        "a flat 'triangle' like (1, 2, 3) is accepted (the sum of two sides must be GREATER than the third)."),
    'isosceles_misses_last_pair': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c:
        return "isosceles"
    return "scalene"''',
        'isosceles is missed when only the last two sides are equal ((4, 3, 3) is called scalene).'),
    'middle_inequality_missing': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or b + c <= a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"''',
        'the inequality a + c > b is not checked ((2, 5, 2) is accepted).'),
    'last_inequality_missing': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"''',
        'the inequality b + c > a is not checked ((5, 2, 2) is accepted).'),
    'isosceles_only_first_pair': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b:
        return "isosceles"
    return "scalene"''',
        'isosceles is only detected when the first two sides are equal ((3, 4, 3) and (4, 3, 3) fail).'),
    'isosceles_before_equilateral': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b or a == c or b == c:
        return "isosceles"
    if a == b == c:
        return "equilateral"
    return "scalene"''',
        'an equilateral triangle is reported as isosceles.'),
    'only_one_inequality': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c:
        return "invalid"
    if a == b == c:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"''',
        'only the inequality a + b > c is checked; a long first side such as (5, 2, 2) is accepted.'),
    'equilateral_needs_a_equals_b_only': (r'''def triangle_kind(a, b, c):
    """Name the triangle with sides a, b, c: 'equilateral', 'isosceles', 'scalene' or 'invalid'."""
    if min(a, b, c) <= 0 or a + b <= c or a + c <= b or b + c <= a:
        return "invalid"
    if a == b and b != 7:
        return "equilateral"
    if a == b or a == c or b == c:
        return "isosceles"
    return "scalene"''',
        'equilateral is decided by comparing only two sides, so (3, 3, 4) is called equilateral.'),
}

MIN_TESTS = 1


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

def _parametrize_calls():
    found = []
    for node in ast.walk(TREE):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "parametrize":
            found.append(node)
    return found


def test_you_use_one_parametrized_test_not_copy_paste():
    assert _parametrize_calls(), "Use @pytest.mark.parametrize (import pytest first) to replace the copy-pasted tests."
    assert len(TESTS) <= 2, (
        f"You have {len(TESTS)} test functions. One parametrized test function (plus at most one more) "
        "replaces the copy-pasted ones; do not keep the old copies.")


def test_every_case_has_a_readable_id():
    calls = _parametrize_calls()
    has_ids = any(any(k.arg == "ids" for k in c.keywords) for c in calls)
    has_param_ids = any(isinstance(n, ast.Call) and any(k.arg == "id" for k in n.keywords)
                        and getattr(n.func, "attr", getattr(n.func, "id", "")) == "param"
                        for n in ast.walk(TREE))
    assert has_ids or has_param_ids, (
        "Give the cases names: parametrize(..., ids=[...]) or pytest.param(..., id='...'). "
        "Without them a failure says 'test_kind[3-3-3-equilateral]' instead of what the case means.")


def test_you_have_enough_cases():
    code, out, results = run_suite(CORRECT)
    assert code == 0, "Fix the failing tests first."
    assert len(results) >= 9, (
        f"Only {len(results)} test cases ran. Cover the three kinds, the order of the sides, "
        "and several invalid shapes: aim for at least 9 rows in your table.")
    assert all("[" in name for name in results), "Each case should be a parametrized one, like test_kind[equilateral]."
    assert all(not name.split("[")[1].rstrip("]").replace("-", "").replace(".", "").isdigit() for name in results), (
        "Some case ids are just numbers. Use readable ids.")


def test_catches_degenerate_is_valid():
    caught('degenerate_is_valid')


def test_catches_isosceles_misses_last_pair():
    caught('isosceles_misses_last_pair')


def test_catches_middle_inequality_missing():
    caught('middle_inequality_missing')


def test_catches_last_inequality_missing():
    caught('last_inequality_missing')


def test_catches_isosceles_only_first_pair():
    caught('isosceles_only_first_pair')


def test_catches_isosceles_before_equilateral():
    caught('isosceles_before_equilateral')


def test_catches_only_one_inequality():
    caught('only_one_inequality')


def test_catches_equilateral_needs_a_equals_b_only():
    caught('equilateral_needs_a_equals_b_only')
