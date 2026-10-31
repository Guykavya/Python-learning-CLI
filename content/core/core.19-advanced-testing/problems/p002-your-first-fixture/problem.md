# Your first fixture: cart

When five tests all begin with the same three lines of setup, move those lines into a
**fixture**: a function marked `@pytest.fixture`. A test that names the fixture as a parameter
receives what the fixture returns, and every test gets a **fresh** one.

The code under test is this `Cart` (save it as `target.py` next to your `solution.py` to try
your tests):

```python
class Cart:
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
        return sum(price * qty for price, qty in self.items.values())
```

In `solution.py` write

1. a fixture called **`cart`** that returns a `Cart` already holding **2 apples at 1.50** and
   **1 bread at 3.00**, and
2. at least **five tests** (functions starting with `test_`), at least four of which take `cart`
   as a parameter. The tests must **not** call `Cart()` themselves.

Your tests must pass on the correct `Cart` and **fail** on each of six buggy versions that the
checker tries (it names the bug that survives). Give each `assert` a message.

**Example of one test**

```python
def test_total_counts_every_unit(cart):
    assert cart.total() == 6.0, "2 apples at 1.50 plus 1 bread at 3.00 is 6.00."
```
