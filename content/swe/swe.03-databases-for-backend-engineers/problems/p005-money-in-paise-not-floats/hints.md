## Hint 1

Which standard-library type does exact decimal arithmetic? How do you turn rupees into paise without going through a float?

## Hint 2

Multiply the `Decimal` by 100, then round to an integer with `quantize(Decimal("1"), rounding=ROUND_HALF_UP)`. `Decimal("abc")` raises `InvalidOperation`; turn it into `ValueError`. `Decimal("nan")` parses fine, so check `is_finite()`.

## Hint 3

```text
amount = Decimal(text.strip())  (InvalidOperation or non-finite -> ValueError)
return int((amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
order_total = sum(qty * unit for qty, unit in lines)
```
