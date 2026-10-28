# An order with computed totals

In a shop's order, the subtotal, discount, tax, shipping and total all depend on the lines and the
discount. If you **store** them, they go stale the moment a line is added. If you **compute** them
in properties, they are always right. Write the class `Order` in `solution.py`.

**Class attributes** (settings shared by all orders):

```python
TAX_RATE = 0.05            # 5% tax
SHIPPING = 40              # shipping fee
FREE_SHIPPING_FROM = 500   # no fee when (subtotal - discount) is at least this
COUPONS = {"WELCOME10": 10, "FEST25": 25, "HALF": 50}
```

**`Order(customer)`** stores `customer` and starts with no lines, a discount of 0 percent, and not
placed.

- `add_line(name, unit_price, qty=1)`: `unit_price` a number of 0 or more, `qty` an `int` of 1 or
  more, otherwise `ValueError`. Adds the line.
- `discount_percent`: a property **with a setter**. The value must be a number from 0 to 50
  (both included), otherwise `ValueError`.
- `apply_coupon(code)`: sets `discount_percent` from `COUPONS` (through the property). An unknown
  code raises `KeyError`.
- `place()`: marks the order as placed. After that, `add_line`, setting `discount_percent` and
  `apply_coupon` raise `RuntimeError("order already placed")`. Placing an empty order raises
  `ValueError`. Placing twice raises `RuntimeError` too.
- `placed`: read-only property, `True`/`False`.

**Computed, read-only properties** (each rounded with `round(x, 2)`):

- `subtotal`: sum of `unit_price * qty`.
- `discount`: `subtotal * discount_percent / 100`.
- `tax`: `(subtotal - discount) * TAX_RATE`.
- `shipping`: `0` for an order with no lines; `0` if `subtotal - discount` is at least
  `FREE_SHIPPING_FROM`; otherwise `SHIPPING`.
- `total`: `subtotal - discount + tax + shipping`.

Setting any of these five raises `AttributeError` (a property without a setter does that).

**Example**

```python
o = Order("Asha")
o.add_line("pen", 10, 5)
o.add_line("book", 150)
o.subtotal, o.shipping, o.total        # (200, 40, 250.0)
o.apply_coupon("WELCOME10")
o.discount_percent                     # 10
o.discount, o.tax, o.total             # (20.0, 9.0, 229.0)
o.add_line("bag", 400)
o.shipping, o.total                    # (0, 567.0)   540 after discount, so no fee
o.discount_percent = 60                # ValueError
o.place()
o.add_line("ink", 5)                   # RuntimeError: order already placed
o.total = 10                           # AttributeError
```
