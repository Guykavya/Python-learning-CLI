## Hint 1

What is the exact value stored for `float("2.675")`? Try `Decimal(2.675)` in the REPL to see it.

## Hint 2

`Decimal(text)` stores the decimal digits exactly. `quantize(Decimal("0.01"), rounding=...)`
rounds to 2 places with the rule you choose.

## Hint 3

```
cent = Decimal("0.01")
print(f"half up: {Decimal(text).quantize(cent, rounding=ROUND_HALF_UP)}")
print(f"half even: {Decimal(text).quantize(cent, rounding=ROUND_HALF_EVEN)}")
```
