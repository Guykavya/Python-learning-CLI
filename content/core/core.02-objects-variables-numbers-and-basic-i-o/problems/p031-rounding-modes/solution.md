## Approach

Compare a rounding that starts from a binary approximation with two roundings that start from
the exact decimal value.

## Code

```python
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN

text = input()
cent = Decimal("0.01")
print(f"float round: {round(float(text), 2):.2f}")
print(f"half up: {Decimal(text).quantize(cent, rounding=ROUND_HALF_UP)}")
print(f"half even: {Decimal(text).quantize(cent, rounding=ROUND_HALF_EVEN)}")
```

## What you learn from the outputs

- `round()` on a float uses half-even, but the float is usually not exactly a tie. `2.675` is stored
  slightly below, so it goes down. `0.125` is exactly representable (it is 1/8), so it is a real tie
  and goes to the even digit: `0.12`.
- `ROUND_HALF_UP` sends ties away from zero: `2.675 -> 2.68`, `-2.675 -> -2.68`.
- `ROUND_HALF_EVEN` (banker's rounding) sends ties to the even digit. Over many values, it does not
  push totals upward, which is why it is the default in Decimal and in `round()`.

## Another way

`round(Decimal(text), 2)` also works and uses the context rounding, which is half-even by default.
