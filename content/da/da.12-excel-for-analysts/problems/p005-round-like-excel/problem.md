# Round like Excel

Chapter sections 4.1 and 11.6. Excel's `ROUND` gives different answers from Python's `round` in two ways:

1. halves go **away from zero** (`ROUND(2.5, 0)` is 3, Python's `round(2.5)` is 2: half to even);
2. Excel looks at the number **at 15 significant digits** before rounding. The float `1.005` is really stored as `1.00499999999999989...`, so Python's `round(1.005, 2)` gives `1.0`, but Excel sees `1.00500000000000` and gives `1.01`.

Write `xl_round(x, n=0)`:

- take the value with **15 significant digits** (`format(float(x), ".15g")`), as a `decimal.Decimal`;
- round to `n` decimal places with `ROUND_HALF_UP` (which in `decimal` means **away from zero**, also for negative numbers);
- `n` may be negative (round to tens, hundreds): `xl_round(1250, -2)` is `1300.0`;
- return a plain `float`.

## Example

```python
xl_round(2.5)          # 3.0
xl_round(-2.5)         # -3.0
xl_round(1.005, 2)     # 1.01      (Python: round(1.005, 2) == 1.0)
```
