## Approach

Decimal arithmetic avoids the binary representation error; `ROUND_HALF_UP` rounds ties away from zero. Reading at 15 significant digits reproduces what Excel does with the stored double.

## Code

```python
from decimal import Decimal, ROUND_HALF_UP


def xl_round(x, n=0):
    d = Decimal(format(float(x), ".15g"))
    if n >= 0:
        return float(d.quantize(Decimal(1).scaleb(-int(n)), rounding=ROUND_HALF_UP))
    f = Decimal(10) ** -int(n)
    return float((d / f).quantize(Decimal(1), rounding=ROUND_HALF_UP) * f)
```

## Complexity

O(1).

## Another way

`Decimal(str(x))` (the shortest repr) also gives `1.005`, but 15 significant digits is the documented behaviour of Excel and handles results of arithmetic such as `0.1 + 0.2`.
