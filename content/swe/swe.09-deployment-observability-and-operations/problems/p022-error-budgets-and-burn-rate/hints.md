## Hint 1

The budget is the number of failures you may afford: what fraction of `total` is allowed to fail with a 99.9% SLO? The burn rate compares **how fast you are failing** (failed / total) with **how fast you may fail** (1 - slo). If the two are equal, what number do you get?

## Hint 2

```text
allowed = total * (1 - slo);  remaining = allowed - failed;  share = remaining / allowed  (1.0 if total == 0)
burn_rate = round((failed / total) / (1 - slo), 9)           (0.0 if total == 0)
burn_alerts: "fast-burn" if burn_rate(1h window) >= 14.4;  "slow-burn" if burn_rate(6h window) >= 6.0
```

The `round(..., 9)` is there because `1440 / 100000 / 0.001` is not exactly 14.4 in floating point.
