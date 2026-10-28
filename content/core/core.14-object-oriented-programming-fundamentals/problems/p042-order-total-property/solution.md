## Approach

**Store the facts, compute the rest.** The order stores three facts: `_lines`, `_discount_percent`,
`_placed`. `subtotal`, `discount`, `tax`, `shipping` and `total` are **computed properties**
(chapter section 8): reading `o.total` runs a method, so the answer always matches the current lines.
There is no "forgot to update the total" bug, because there is no stored total.

Computed properties build on each other: `total` uses `tax` and `shipping`, which use `discount`,
which uses `subtotal`. Each piece of the rule lives in one small, readable place.

**A validated property.** `discount_percent` has a setter that checks the range and that the order
is still open. `apply_coupon` assigns through the property, so it gets the same checks for free.

**Class attributes for settings.** `TAX_RATE`, `SHIPPING`, `FREE_SHIPPING_FROM` and `COUPONS` are
the same for every order, so they live on the class (section 5). The methods read them through
`self`, so a subclass (say, `ExpressOrder` with `SHIPPING = 90`) could change one setting by
overriding a single class attribute.

**Locking.** `_check_open()` is called first in every method that changes the order.

## Code

```python
class Order:
    TAX_RATE = 0.05
    SHIPPING = 40
    FREE_SHIPPING_FROM = 500
    COUPONS = {"WELCOME10": 10, "FEST25": 25, "HALF": 50}

    def __init__(self, customer):
        self.customer = customer
        self._lines = []            # (name, unit_price, qty)
        self._discount_percent = 0
        self._placed = False

    def _check_open(self):
        if self._placed:
            raise RuntimeError("order already placed")

    def add_line(self, name, unit_price, qty=1):
        self._check_open()
        if not isinstance(unit_price, (int, float)) or unit_price < 0:
            raise ValueError(f"unit_price must be a number of at least 0, got {unit_price!r}")
        if not isinstance(qty, int) or qty < 1:
            raise ValueError(f"qty must be a whole number of at least 1, got {qty!r}")
        self._lines.append((name, unit_price, qty))

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        self._check_open()
        if not isinstance(value, (int, float)) or not 0 <= value <= 50:
            raise ValueError(f"discount_percent must be from 0 to 50, got {value!r}")
        self._discount_percent = value

    def apply_coupon(self, code):
        self._check_open()
        self.discount_percent = self.COUPONS[code]      # KeyError for an unknown code

    def place(self):
        self._check_open()
        if not self._lines:
            raise ValueError("cannot place an empty order")
        self._placed = True

    @property
    def placed(self):
        return self._placed

    @property
    def subtotal(self):
        return round(sum(price * qty for _, price, qty in self._lines), 2)

    @property
    def discount(self):
        return round(self.subtotal * self.discount_percent / 100, 2)

    @property
    def tax(self):
        return round((self.subtotal - self.discount) * self.TAX_RATE, 2)

    @property
    def shipping(self):
        if not self._lines or self.subtotal - self.discount >= self.FREE_SHIPPING_FROM:
            return 0
        return self.SHIPPING

    @property
    def total(self):
        return round(self.subtotal - self.discount + self.tax + self.shipping, 2)
```

## Complexity

Each computed property is O(n) for n lines (it sums the lines again). `total` calls `subtotal`
several times, so it does a few passes; for a shopping order that is nothing.

## Another way

If the lines were huge and `total` were read very often, you could cache the subtotal and clear the
cache in `add_line` (`functools.cached_property` helps when the value never changes). Caching brings
back the "stale value" risk that computed properties remove, so do it only when measuring shows a
need. Real shops also store money as integer paise (see the `Money` problem) to avoid float rounding.
