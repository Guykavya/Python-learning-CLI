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

CORRECT = 'def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)'

MUTANTS = {
    'name_not_lowercased': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'add_item does not lower-case the name.'),
    'name_not_stripped': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'add_item does not strip spaces from the name.'),
    'zero_quantity_allowed': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty < 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'add_item accepts a quantity of 0.'),
    'add_replaces_instead_of_adding': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'adding to an existing item replaces the quantity instead of adding to it.'),
    'empty_name_allowed': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'add_item accepts an empty name.'),
    'unknown_item_wrong_error': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise ValueError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'removing an unknown item raises ValueError instead of KeyError.'),
    'cannot_remove_all': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty >= inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        "removing exactly the whole stock is rejected as 'not enough stock'."),
    'zero_item_kept': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'an item whose quantity reaches 0 stays in the dict.'),
    'total_counts_items': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return len(inventory)\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'total_items counts the kinds of items instead of adding the quantities.'),
    'low_stock_uses_le': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] <= limit:\n            names.append(name)\n    return sorted(names)',
        'low_stock includes items whose quantity equals the limit.'),
    'low_stock_unsorted': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    if qty > inventory[key]:\n        raise ValueError("not enough stock")\n    inventory[key] -= qty\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return names',
        'low_stock returns the names in dict order instead of sorted order.'),
    'remove_changes_stock_before_check': ('def add_item(inventory, name, qty):\n    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    key = name.strip().lower()\n    if key == "":\n        raise ValueError("name must not be empty")\n    inventory[key] = inventory.get(key, 0) + qty\n    return inventory[key]\n\n\ndef remove_item(inventory, name, qty):\n    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""\n    key = name.strip().lower()\n    if key not in inventory:\n        raise KeyError(key)\n    if qty <= 0:\n        raise ValueError("quantity must be positive")\n    inventory[key] -= qty\n    if inventory[key] < 0:\n        raise ValueError("not enough stock")\n    if inventory[key] == 0:\n        del inventory[key]\n        return 0\n    return inventory[key]\n\n\ndef total_items(inventory):\n    """Total number of units over all items."""\n    return sum(inventory.values())\n\n\ndef low_stock(inventory, limit):\n    """Sorted list of the names whose quantity is below limit."""\n    names = []\n    for name in inventory:\n        if inventory[name] < limit:\n            names.append(name)\n    return sorted(names)',
        'a failed removal (too much) has already changed the stock before raising.'),
}

MIN_TESTS = 10


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


def test_catches_name_not_lowercased():
    caught('name_not_lowercased')

def test_catches_name_not_stripped():
    caught('name_not_stripped')

def test_catches_zero_quantity_allowed():
    caught('zero_quantity_allowed')

def test_catches_add_replaces_instead_of_adding():
    caught('add_replaces_instead_of_adding')

def test_catches_empty_name_allowed():
    caught('empty_name_allowed')

def test_catches_unknown_item_wrong_error():
    caught('unknown_item_wrong_error')

def test_catches_cannot_remove_all():
    caught('cannot_remove_all')

def test_catches_zero_item_kept():
    caught('zero_item_kept')

def test_catches_total_counts_items():
    caught('total_counts_items')

def test_catches_low_stock_uses_le():
    caught('low_stock_uses_le')

def test_catches_low_stock_unsorted():
    caught('low_stock_unsorted')

def test_catches_remove_changes_stock_before_check():
    caught('remove_changes_stock_before_check')


def test_requirement_1():
    assert 'parametrize' in LEARNER_SOURCE, 'Use @pytest.mark.parametrize at least once.'


def test_requirement_2():
    assert 'raises' in LEARNER_SOURCE, 'Use pytest.raises for the error cases.'


def test_requirement_3():
    assert 'match' in LEARNER_SOURCE, 'Use match= to check the message of at least one error.'
