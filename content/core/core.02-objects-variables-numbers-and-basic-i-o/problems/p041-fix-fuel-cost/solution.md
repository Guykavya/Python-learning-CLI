## Approach

Debug one symptom at a time. Compare each line with the specification rather than guessing.

## The bugs

| Line | Bug | Effect |
|---|---|---|
| `distance = int(input())` | `int` cannot read `120.5` | `ValueError` crash |
| `mileage = float(input())` | float, not Decimal | binary errors, and mixing float with Decimal later raises `TypeError` |
| `price = Decimal(float(input()))` | Decimal built from a float | copies the float's error, so 0.15 becomes 0.1499999999999999944... |
| `litres = distance * mileage` | wrong formula | litres should be distance / mileage |
| `round(litres, 2)` | half-even rounding, and no fixed 2 decimals | `0.125` shows as `0.12`; `12.5` shows as `12.5` |
| `sep=""` | removes the space | prints `Cost:1250.00` |
| `cost.quantize(CENT)` | default rounding is half-even | `0.225` becomes `0.22` |

## Fixed code

```python
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
distance = Decimal(input())
mileage = Decimal(input())
price = Decimal(input())
litres = distance / mileage
cost = litres * price
print("Litres:", litres.quantize(CENT, rounding=ROUND_HALF_UP))
print("Cost:", cost.quantize(CENT, rounding=ROUND_HALF_UP))
```

## Why round only at the end

If you round litres to 12.50 first and then multiply, the error from rounding is multiplied by
the price. Keeping the full precision until display avoids that.

## Another way

Set the rounding once for the whole program with `getcontext().rounding = ROUND_HALF_UP`, then
call `quantize(CENT)` without the argument.
