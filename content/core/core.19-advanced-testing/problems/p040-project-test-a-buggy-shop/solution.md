## Approach

Read the specification as a list of **testable sentences** and give each sentence at least one test, aimed at the boundary where an
off-by-one or wrong operator would show:

| Spec sentence | Test | Bugs it kills |
|---|---|---|
| stock adds up; unknown is 0 | `test_stock_adds_up_and_unknown_is_zero` | `stock_of_unknown_item_crashes` |
| qty must be positive | parametrized 0 and -1 for stock and cart | `stock_accepts_zero`, `cart_accepts_zero_quantity` |
| exactly all stock can be removed | `test_can_remove_exactly_all_stock` and the checkout twin | `cannot_remove_last_unit` |
| adding twice adds | `test_cart_merges_same_item_and_sums` | `cart_add_replaces_quantity` |
| remove of a missing item raises | `test_cart_remove` | `cart_remove_missing_is_silent` |
| SAVE10 from 5000, rounded down | parametrize 4999, 5000, 5019 | `save10_needs_more_than_5000`, `save10_rounds_up` |
| FIVER from 1000 | parametrize 999, 1000 | `fiver_needs_more_than_1000` |
| unknown code | `pytest.raises(ValueError)` | `unknown_code_ignored` |
| shipping on the order **after** discount | lamp + book + 2 pens with SAVE10: 4950 | `free_shipping_ignores_discount` |
| free from exactly 5000 | `shipping_cents(5000)` and a receipt | `free_shipping_needs_more_than_5000` |
| tax only on goods, half up | exact receipts; `tax_cents(1007)` | `tax_includes_shipping`, `tax_rounds_down` |
| all or nothing | good item first, bad item second, check stock and cart | `checkout_partly_removes_stock` |
| cart emptied; empty cart refused | stock and cart after checkout; `pytest.raises` | `checkout_keeps_the_cart`, `checkout_accepts_empty_cart` |

Notice the pattern: **unit tests for each rule** (`discount_cents`, `shipping_cents`, `tax_cents`) pin the numbers; **checkout
tests with whole receipts** pin how the rules are combined. The combination bugs (`free_shipping_ignores_discount`, `tax_includes_shipping`) cannot be seen
by the unit tests, since each rule is right on its own and the mistake is in what is passed to it.

## Code

The full reference suite is in `reference.py` next to this problem; a shortened version of its structure:

```python
import pytest

import shop

PRICES = {"pen": 150, "book": 1200, "mug": 1000, "lamp": 4000}


@pytest.fixture
def inv():
    inventory = shop.Inventory()
    for sku in PRICES:
        inventory.add_stock(sku, 5)
    return inventory


@pytest.fixture
def cart():
    return shop.Cart(PRICES)


@pytest.mark.parametrize("subtotal, code, expected", [
    (4999, "SAVE10", 0), (5000, "SAVE10", 500), (5019, "SAVE10", 501),
    (999, "FIVER", 0), (1000, "FIVER", 500), (9999, None, 0),
])
def test_discount_cents(subtotal, code, expected):
    assert shop.discount_cents(subtotal, code) == expected


def test_checkout_shipping_is_decided_after_the_discount(inv, cart):
    cart.add("lamp"); cart.add("book"); cart.add("pen", 2)
    receipt = shop.checkout(cart, inv, "SAVE10")
    assert receipt == {"subtotal": 5500, "discount": 550, "shipping": 499, "tax": 396, "total": 5845}


def test_checkout_out_of_stock_changes_nothing(inv, cart):
    cart.add("pen"); cart.add("book", 6)
    with pytest.raises(shop.OutOfStock):
        shop.checkout(cart, inv)
    assert inv.stock("pen") == 5 and inv.stock("book") == 5
    assert cart.items == {"pen": 1, "book": 6}
```

## Cost

About 35 tests; each runs in microseconds. The cost that matters is **thinking time**: choosing the few inputs that sit on the borders.

## Another way

Add `hypothesis` for the arithmetic: for every subtotal, `total == subtotal - discount + shipping + tax`, and `discount <= subtotal`. These
properties would hold for several of the buggy versions too, so they cannot replace the exact-receipt tests, but they cover borders you did not
think of. Another habit worth keeping: after you finish, re-read the specification for a rule you have **no** test for.
