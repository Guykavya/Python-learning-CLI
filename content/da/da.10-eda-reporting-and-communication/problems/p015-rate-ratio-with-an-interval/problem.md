# Rate ratio with an interval

Chapter section 5.2. Customers with a recent late box left at 21 per 1,000 customer-weeks, those without at 7.8. The **rate ratio** says "how many times as often":

```text
rr = (e1 / n1) / (e0 / n0)
se = sqrt(1/e1 - 1/n1 + 1/e0 - 1/n0)              (on the log scale)
95% CI = rr x exp(-1.96 x se)  to  rr x exp(+1.96 x se)
```

`e1` events among `n1` in the exposed group, `e0` among `n0` in the comparison group. Write `rate_ratio(e1, n1, e0, n0)` that returns `(rr, low, high)` as floats.

- The interval is built on the log scale, so it is **not symmetric** around `rr`.
- With **zero events** in either group the formula breaks: raise `ValueError("need at least one event in each group")`.
- More events than people is impossible: if `e1 > n1` or `e0 > n0`, raise `ValueError("events cannot exceed the group size")`.

## Example

`rate_ratio(20, 1000, 10, 1000)` returns about `(2.0, 0.941, 4.251)`: twice the rate, but the interval includes 1, so this small sample cannot rule out "no difference".
