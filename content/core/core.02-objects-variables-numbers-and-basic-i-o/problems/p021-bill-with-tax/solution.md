## Approach

Do all the money arithmetic in base 10 with `Decimal`, and round explicitly with the rule
the business uses. Never let a float touch the amounts.

## Code

```python
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
price = Decimal(input())
qty = int(input())
rate = Decimal(input())
subtotal = (price * qty).quantize(CENT, rounding=ROUND_HALF_UP)
tax = (subtotal * rate / 100).quantize(CENT, rounding=ROUND_HALF_UP)
total = subtotal + tax
print(f"Subtotal: {subtotal}")
print(f"Tax: {tax}")
print(f"Total: {total}")
```

## Why each piece matters

- `Decimal(input())` builds the exact value the user typed. `Decimal(float(...))` would copy the float error.
- `quantize(CENT)` fixes the number of decimals, so `5 * 2` prints as `10.00`, not `10`.
- The default rounding of Decimal is `ROUND_HALF_EVEN` (banker's rounding): `0.025` becomes `0.02`.
  Shops normally use half up, so we ask for it.
- Multiplying a Decimal by an `int` is fine; mixing Decimal with a `float` raises `TypeError`.

## Another way

Work in whole paise with `int`: `paise = int(Decimal(price) * 100)`. Integers are exact too,
but you then have to do the half-up rounding of the tax by hand.
