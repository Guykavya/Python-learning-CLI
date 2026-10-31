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

CORRECT = r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return price_with_tax(max(net - discount, 0))'''

MUTANTS = {
    'tax_before_discount': (r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return max(price_with_tax(net) - discount, 0)''',
        'tax is added before the discount is taken off (the order matters).'),
    'ignores_discount': (r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return price_with_tax(net)''',
        'the discount is never applied.'),
    'no_floor_at_zero': (r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return price_with_tax(net - discount)''',
        'a discount bigger than the price gives a negative total.'),
    'hardcoded_rate': (r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * 1.2, 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return price_with_tax(max(net - discount, 0))''',
        'price_with_tax ignores TAX_RATE (it hard-codes 1.2).'),
    'rounds_to_one_decimal': (r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 1)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount(code)
    return price_with_tax(max(net - discount, 0))''',
        'the price is rounded to one decimal instead of two (cents are lost).'),
    'wrong_code_sent': (r'''TAX_RATE = 0.2


def fetch_discount(code):
    """Ask the discount server how much the code is worth (slow, needs the network)."""
    raise RuntimeError("no network in tests: patch fetch_discount")


def price_with_tax(net):
    return round(net * (1 + TAX_RATE), 2)


def checkout(net, code):
    """Take the discount off, then add tax. The price never goes below zero."""
    discount = fetch_discount("")
    return price_with_tax(max(net - discount, 0))''',
        "fetch_discount is called with the wrong code (the user's code is not passed on)."),
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

def test_you_use_monkeypatch_and_import_the_module():
    assert "import target" in LEARNER_SOURCE, (
        "Write `import target` (not `from target import ...`) so monkeypatch.setattr(target, 'TAX_RATE', ...) "
        "changes the very name the functions look up.")
    users = [n for n in TESTS if "monkeypatch" in arg_names(n)]
    assert len(users) >= 4, "Take the monkeypatch fixture in at least four tests, found %d." % len(users)


def test_catches_tax_before_discount():
    caught('tax_before_discount')


def test_catches_ignores_discount():
    caught('ignores_discount')


def test_catches_no_floor_at_zero():
    caught('no_floor_at_zero')


def test_catches_hardcoded_rate():
    caught('hardcoded_rate')


def test_catches_rounds_to_one_decimal():
    caught('rounds_to_one_decimal')


def test_catches_wrong_code_sent():
    caught('wrong_code_sent')
