## Approach

```python
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def to_paise(text):
    try:
        amount = Decimal(text.strip())
    except (InvalidOperation, AttributeError):
        raise ValueError(f"not an amount: {text!r}") from None
    if not amount.is_finite():
        raise ValueError(f"not an amount: {text!r}")
    return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def order_total(lines):
    return sum(qty * unit_paise for qty, unit_paise in lines)
```

`Decimal("12.345")` is exactly 12.345 (not the nearest binary number), so `* 100` gives exactly `1234.5`, and `ROUND_HALF_UP` turns that into `1235`. Python's built-in `round()` uses banker's rounding (`round(2.5)` is 2), which is **not** what a shop wants. With integer paise, addition is exact: `10 + 20 == 30`.

Example: `order_total([(2, 25000), (1, 30000)])` is `50000 + 30000 = 80000` paise, or Rs. 800.00.

## Complexity

`O(number of lines)`.

## Another way

Use `int(round(float(text) * 100))`: it looks right and is wrong for amounts such as `1.005`, because the float is really `1.00499999999999989...`.

## Why it matters

Every price, tax and total in this module is an integer number of paise; only the display code divides by 100.
