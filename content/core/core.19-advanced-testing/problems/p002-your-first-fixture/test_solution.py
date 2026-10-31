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

CORRECT = r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        del self.items[name]

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self):
        return sum(price * qty for price, qty in self.items.values())'''

MUTANTS = {
    'total_ignores_quantity': (r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        del self.items[name]

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self):
        return sum(price for price, qty in self.items.values())''',
        'total() ignores the quantity (2 apples at 1.50 are counted once).'),
    'add_overwrites_existing': (r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name] = [price, qty]
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        del self.items[name]

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self):
        return sum(price * qty for price, qty in self.items.values())''',
        'adding an item that is already in the cart replaces it instead of adding to its quantity.'),
    'remove_does_nothing': (r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        pass

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self):
        return sum(price * qty for price, qty in self.items.values())''',
        'remove() does not remove anything.'),
    'remove_missing_is_silent': (r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        self.items.pop(name, None)

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self):
        return sum(price * qty for price, qty in self.items.values())''',
        'removing an item that is not in the cart should raise KeyError but passes silently.'),
    'count_counts_lines': (r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if qty <= 0:
            raise ValueError("qty must be positive")
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        del self.items[name]

    def count(self):
        return len(self.items)

    def total(self):
        return sum(price * qty for price, qty in self.items.values())''',
        'count() counts distinct items instead of units (2 apples + 1 bread = 3).'),
    'zero_quantity_allowed': (r'''class Cart:
    """A shopping cart: items are stored as name -> [price, quantity]."""

    def __init__(self):
        self.items = {}

    def add(self, name, price, qty=1):
        if name in self.items:
            self.items[name][1] += qty
        else:
            self.items[name] = [price, qty]

    def remove(self, name):
        del self.items[name]

    def count(self):
        return sum(qty for _, qty in self.items.values())

    def total(self):
        return sum(price * qty for price, qty in self.items.values())''',
        'add(..., qty=0) is accepted although a quantity must be positive.'),
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

def _is_fixture(dec):
    node = dec.func if isinstance(dec, ast.Call) else dec
    return (isinstance(node, ast.Attribute) and node.attr == "fixture") or (
        isinstance(node, ast.Name) and node.id == "fixture")


def test_you_wrote_a_fixture_called_cart():
    fixtures = [n for n in ast.walk(TREE) if isinstance(n, ast.FunctionDef)
                and any(_is_fixture(d) for d in n.decorator_list)]
    assert any(f.name == "cart" for f in fixtures), (
        "Write a function called cart and decorate it with @pytest.fixture (import pytest first).")


def test_the_tests_use_the_fixture_instead_of_building_carts():
    users = [n for n in TESTS if "cart" in arg_names(n)]
    assert len(users) >= 4, (
        "At least four test functions must take cart as a parameter, "
        f"e.g. def test_total(cart):. Found {len(users)}.")
    for fn in TESTS:
        for node in ast.walk(fn):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Cart":
                raise AssertionError(
                    f"{fn.name} builds its own Cart(). Creating the cart is the fixture's job; "
                    "take cart as a parameter instead.")


def test_the_fixture_gives_a_prefilled_cart():
    code, out, results = run_suite(CORRECT)
    assert code == 0, "Fix the failing tests first."
    # the fixture must hand out 2 apples (1.50) and 1 bread (3.00): totals 6.0 and 3 items
    probe = LEARNER_SOURCE + """

def test_probe_fixture_content(cart):
    assert cart.items == {"apple": [1.5, 2], "bread": [3.0, 1]}, "fixture must hold 2 apples at 1.50 and 1 bread at 3.00"
"""
    with tempfile.TemporaryDirectory(prefix="learn-fx-") as tmp:
        tmp = Path(tmp)
        (tmp / "target.py").write_text(CORRECT)
        (tmp / "test_probe.py").write_text(probe)
        env = dict(os.environ, PYTHONPATH=str(tmp), PYTHONDONTWRITEBYTECODE="1")
        proc = subprocess.run([sys.executable, "-m", "pytest", "test_probe.py", "-q", "--no-header",
                               "-p", "no:cacheprovider", "-k", "test_probe_fixture_content", "--tb=line"],
                              cwd=tmp, capture_output=True, text=True, timeout=60, env=env)
    assert proc.returncode == 0, (
        "The cart fixture must return a Cart that already holds 2 apples at 1.50 and 1 bread at 3.00 "
        "(use cart.add(...) inside the fixture). pytest said:\n" + (proc.stdout + proc.stderr)[-500:])


def test_catches_total_ignores_quantity():
    caught('total_ignores_quantity')


def test_catches_add_overwrites_existing():
    caught('add_overwrites_existing')


def test_catches_remove_does_nothing():
    caught('remove_does_nothing')


def test_catches_remove_missing_is_silent():
    caught('remove_missing_is_silent')


def test_catches_count_counts_lines():
    caught('count_counts_lines')


def test_catches_zero_quantity_allowed():
    caught('zero_quantity_allowed')
