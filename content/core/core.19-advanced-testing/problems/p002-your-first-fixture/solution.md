## Approach

The fixture builds the shared starting state once per test. Every test then checks **one**
behaviour of `Cart` starting from that state. The six bugs live in different methods, so each
needs a test that reaches that method with data where the buggy answer differs.

## Code

```python
import pytest

from target import Cart


@pytest.fixture
def cart():
    c = Cart()
    c.add("apple", 1.5, 2)
    c.add("bread", 3.0)
    return c


def test_total_counts_every_unit(cart):
    assert cart.total() == 6.0


def test_count_is_in_units(cart):
    assert cart.count() == 3


def test_adding_an_existing_item_adds_quantity(cart):
    cart.add("apple", 1.5, 3)
    assert cart.count() == 6


def test_remove_takes_the_whole_line_away(cart):
    cart.remove("bread")
    assert cart.total() == 3.0


def test_removing_a_missing_item_raises(cart):
    with pytest.raises(KeyError):
        cart.remove("milk")


def test_zero_quantity_is_rejected(cart):
    with pytest.raises(ValueError):
        cart.add("milk", 1.0, 0)
```

## Cost

The fixture runs once per test (function scope), so six tests build six carts. Cheap here; for
expensive setup you would widen the scope (chapter section 3).

## Another way

A fixture that returns an **empty** cart plus small helper calls in each test is also fine. A
prefilled cart is shorter when most tests need the same items.
