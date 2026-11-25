## Hint 1

`Decimal(format(x, ".15g"))` builds the decimal number Excel "sees". Which `Decimal.quantize` argument sets the number of places, and which rounding mode means "half away from zero"?

## Hint 2

```text
d = Decimal(format(float(x), ".15g"))
n >= 0: float(d.quantize(Decimal(1).scaleb(-n), rounding=ROUND_HALF_UP))
n < 0:  f = Decimal(10) ** -n; float((d / f).quantize(Decimal(1), rounding=ROUND_HALF_UP) * f)
```
