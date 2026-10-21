# Build: a test suite for an inventory module

This is the assessed build for the module, and a small version of the module project (a test
suite for your own earlier projects). Below is a small inventory module: four functions that work
on a dict `{name: quantity}`. Write a **complete pytest suite** for it in `solution.py`, importing
with `from target import add_item, remove_item, total_items, low_stock`.

```python
def add_item(inventory, name, qty):
    """Add qty of an item. Names are stripped and lower-cased. Return the new quantity of that item."""
    if qty <= 0:
        raise ValueError("quantity must be positive")
    key = name.strip().lower()
    if key == "":
        raise ValueError("name must not be empty")
    inventory[key] = inventory.get(key, 0) + qty
    return inventory[key]


def remove_item(inventory, name, qty):
    """Remove qty of an item. An item whose quantity reaches 0 is deleted. Return what is left."""
    key = name.strip().lower()
    if key not in inventory:
        raise KeyError(key)
    if qty <= 0:
        raise ValueError("quantity must be positive")
    if qty > inventory[key]:
        raise ValueError("not enough stock")
    inventory[key] -= qty
    if inventory[key] == 0:
        del inventory[key]
        return 0
    return inventory[key]


def total_items(inventory):
    """Total number of units over all items."""
    return sum(inventory.values())


def low_stock(inventory, limit):
    """Sorted list of the names whose quantity is below limit."""
    names = []
    for name in inventory:
        if inventory[name] < limit:
            names.append(name)
    return sorted(names)
```

Your suite must

- pass on the correct module;
- fail on **each of twelve** buggy versions of it (normal-case bugs, boundary bugs, error-type
  bugs, a bug that forgets to delete an empty item, and one that changes the stock even when it
  raises);
- contain at least **10 test functions**, at least one `@pytest.mark.parametrize` and at least one
  `pytest.raises(..., match=...)`.

Plan before you write: for each function list the normal case, the boundaries, and every
`raise`. Build a fresh `stock = {}` inside each test so tests stay independent.

**How this is checked.** Your `solution.py` is a file of pytest tests (chapter section 6). The
checker copies it next to the function above (saved as `target.py`) and runs real pytest, first on
the **correct** function (all your tests must pass), then on several **buggy copies** of it (at
least one of your tests must fail on each). Save the function as `target.py` in your folder
and run `python -m pytest solution.py` to try your tests yourself.
