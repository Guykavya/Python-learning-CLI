## Approach

Translate the formula carefully. `**` has higher precedence than `*` and `/`, so the exponent needs brackets.

## Code

```python
p = float(input())
r = float(input())
t = int(input())
n = int(input())
a = p * (1 + r / (100 * n)) ** (n * t)
print(f"Amount: {a:,.2f}")
print(f"Interest: {a - p:,.2f}")
```

## Why floats are acceptable here

This is an estimate that is displayed with 2 decimals, not a ledger. The tiny binary errors
are far below a paisa. For a real bank statement, where each period's interest is rounded and
added, you would use `Decimal` and round at every step.

## Another way

`pow(1 + r / (100 * n), n * t)` is the same as the `**` expression. `math.pow` also works but always returns a float.
