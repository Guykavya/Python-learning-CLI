import ast
import os
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# How this check works: your solution.py is a file of pytest tests. It is copied next to a
# file called shop.py that holds the code under test, and real pytest runs on it.
# First against the CORRECT code (all your tests must pass), then against several BUGGY
# copies (at least one of your tests must fail for each bug).

LEARNER = Path(__file__).with_name("solution.py")
LEARNER_SOURCE = LEARNER.read_text()

MODULE = "shop"
MIN_TESTS = 12
HYPOTHESIS = False

CORRECT = r'''class OutOfStock(Exception):
    """Raised when the inventory does not hold enough of an item."""


TAX_PERCENT = 8
FREE_SHIPPING_FROM = 5000
SHIPPING_FEE = 499


class Inventory:
    def __init__(self):
        self._stock = {}

    def add_stock(self, sku, qty):
        if qty <= 0:
            raise ValueError("qty must be positive")
        self._stock[sku] = self._stock.get(sku, 0) + qty

    def stock(self, sku):
        return self._stock.get(sku, 0)

    def remove_stock(self, sku, qty):
        if self.stock(sku) < qty:
            raise OutOfStock(sku)
        self._stock[sku] -= qty


class Cart:
    def __init__(self, prices):
        self.prices = prices   # sku -> price in cents
        self.items = {}        # sku -> quantity, in the order first added

    def add(self, sku, qty=1):
        if sku not in self.prices:
            raise KeyError(sku)
        if qty <= 0:
            raise ValueError("qty must be positive")
        self.items[sku] = self.items.get(sku, 0) + qty

    def remove(self, sku):
        del self.items[sku]

    def subtotal(self):
        return sum(self.prices[sku] * qty for sku, qty in self.items.items())


def discount_cents(subtotal, code):
    if code is None:
        return 0
    if code == "SAVE10":
        if subtotal >= 5000:
            return subtotal * 10 // 100
        return 0
    if code == "FIVER":
        if subtotal >= 1000:
            return 500
        return 0
    raise ValueError(f"unknown code: {code}")


def shipping_cents(amount):
    if amount == 0:
        return 0
    if amount >= FREE_SHIPPING_FROM:
        return 0
    return SHIPPING_FEE


def tax_cents(amount):
    return (amount * TAX_PERCENT + 50) // 100


def checkout(cart, inventory, code=None):
    if not cart.items:
        raise ValueError("cart is empty")
    for sku, qty in cart.items.items():
        if inventory.stock(sku) < qty:
            raise OutOfStock(sku)
    subtotal = cart.subtotal()
    discount = discount_cents(subtotal, code)
    taxable = subtotal - discount
    shipping = shipping_cents(taxable)
    tax = tax_cents(taxable)
    for sku, qty in cart.items.items():
        inventory.remove_stock(sku, qty)
    cart.items.clear()
    return {
        "subtotal": subtotal,
        "discount": discount,
        "shipping": shipping,
        "tax": tax,
        "total": taxable + shipping + tax,
    }'''

# name -> (text to replace in CORRECT, replacement, what the bug does)
MUTANTS = {'stock_accepts_zero': ('def add_stock(self, sku, qty):\n        if qty <= 0:',
                        'def add_stock(self, sku, qty):\n        if qty < 0:',
                        'Inventory.add_stock(sku, 0) is accepted instead of raising ValueError.'),
 'stock_of_unknown_item_crashes': ('return self._stock.get(sku, 0)',
                                   'return self._stock[sku]',
                                   'Inventory.stock of an item that was never added raises KeyError instead '
                                   'of returning 0.'),
 'cannot_remove_last_unit': ('if self.stock(sku) < qty:\n'
                             '            raise OutOfStock(sku)\n'
                             '        self._stock',
                             'if self.stock(sku) <= qty:\n'
                             '            raise OutOfStock(sku)\n'
                             '        self._stock',
                             'removing exactly all the stock of an item raises OutOfStock (off by one).'),
 'cart_accepts_zero_quantity': ('raise KeyError(sku)\n        if qty <= 0:',
                                'raise KeyError(sku)\n        if qty < 0:',
                                'Cart.add(sku, 0) is accepted instead of raising ValueError.'),
 'cart_add_replaces_quantity': ('self.items[sku] = self.items.get(sku, 0) + qty',
                                'self.items[sku] = qty',
                                'adding the same item twice keeps only the last quantity instead of adding '
                                'them up.'),
 'cart_remove_missing_is_silent': ('del self.items[sku]',
                                   'self.items.pop(sku, None)',
                                   'Cart.remove of an item that is not in the cart is silently accepted '
                                   'instead of raising KeyError.'),
 'save10_needs_more_than_5000': ('if subtotal >= 5000:',
                                 'if subtotal > 5000:',
                                 "SAVE10 does not apply at a subtotal of exactly 5000 (the threshold is 'at "
                                 "least 5000')."),
 'save10_rounds_up': ('return subtotal * 10 // 100',
                      'return (subtotal * 10 + 99) // 100',
                      'SAVE10 rounds the discount up instead of down (a subtotal of 5019 gives 502 instead '
                      'of 501).'),
 'fiver_needs_more_than_1000': ('if subtotal >= 1000:',
                                'if subtotal > 1000:',
                                "FIVER does not apply at a subtotal of exactly 1000 (the threshold is 'at "
                                "least 1000')."),
 'unknown_code_ignored': ('raise ValueError(f"unknown code: {code}")',
                          'return 0',
                          'an unknown discount code gives a discount of 0 instead of raising ValueError.'),
 'free_shipping_ignores_discount': ('shipping = shipping_cents(taxable)',
                                    'shipping = shipping_cents(subtotal)',
                                    'free shipping is decided on the subtotal BEFORE the discount instead of '
                                    'after it.'),
 'free_shipping_needs_more_than_5000': ('if amount >= FREE_SHIPPING_FROM:',
                                        'if amount > FREE_SHIPPING_FROM:',
                                        'an order of exactly 5000 (after discount) still pays shipping; the '
                                        "rule is 'free from 5000'."),
 'tax_includes_shipping': ('tax = tax_cents(taxable)',
                           'tax = tax_cents(taxable + shipping)',
                           'tax is charged on the shipping fee too; only the goods after discount are '
                           'taxed.'),
 'tax_rounds_down': ('return (amount * TAX_PERCENT + 50) // 100',
                     'return amount * TAX_PERCENT // 100',
                     'tax is truncated instead of rounded half up (1007 gives 80 instead of 81).'),
 'checkout_partly_removes_stock': ('    for sku, qty in cart.items.items():\n'
                                   '        if inventory.stock(sku) < qty:\n'
                                   '            raise OutOfStock(sku)\n',
                                   '',
                                   'checkout does not check all items first, so when a later item is out of '
                                   'stock the earlier items have already been taken from the inventory.'),
 'checkout_keeps_the_cart': ('    cart.items.clear()\n',
                             '',
                             'the cart is not emptied after a successful checkout, so a second checkout '
                             'charges again.'),
 'checkout_accepts_empty_cart': ('    if not cart.items:\n        raise ValueError("cart is empty")\n',
                                 '',
                                 'checkout of an empty cart returns a receipt instead of raising '
                                 'ValueError.')}

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

def test_catches_stock_accepts_zero():
    caught('stock_accepts_zero')

def test_catches_stock_of_unknown_item_crashes():
    caught('stock_of_unknown_item_crashes')

def test_catches_cannot_remove_last_unit():
    caught('cannot_remove_last_unit')

def test_catches_cart_accepts_zero_quantity():
    caught('cart_accepts_zero_quantity')

def test_catches_cart_add_replaces_quantity():
    caught('cart_add_replaces_quantity')

def test_catches_cart_remove_missing_is_silent():
    caught('cart_remove_missing_is_silent')

def test_catches_save10_needs_more_than_5000():
    caught('save10_needs_more_than_5000')

def test_catches_save10_rounds_up():
    caught('save10_rounds_up')

def test_catches_fiver_needs_more_than_1000():
    caught('fiver_needs_more_than_1000')

def test_catches_unknown_code_ignored():
    caught('unknown_code_ignored')

def test_catches_free_shipping_ignores_discount():
    caught('free_shipping_ignores_discount')

def test_catches_free_shipping_needs_more_than_5000():
    caught('free_shipping_needs_more_than_5000')

def test_catches_tax_includes_shipping():
    caught('tax_includes_shipping')

def test_catches_tax_rounds_down():
    caught('tax_rounds_down')

def test_catches_checkout_partly_removes_stock():
    caught('checkout_partly_removes_stock')

def test_catches_checkout_keeps_the_cart():
    caught('checkout_keeps_the_cart')

def test_catches_checkout_accepts_empty_cart():
    caught('checkout_accepts_empty_cart')


def test_you_wrote_a_real_suite():
    assert LEARNER_SOURCE.count("def test_") >= 12, "A suite for this much code needs at least a dozen tests."
