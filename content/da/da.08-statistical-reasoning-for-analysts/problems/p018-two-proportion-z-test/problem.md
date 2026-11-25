# Two-proportion z-test

Chapter section 5. Is the conversion of version A different from version B? Under "no difference" both groups share one true rate,
estimated by the **pooled** proportion `p = (kA + kB) / (nA + nB)`. The test statistic is

`z = (pA - pB) / sqrt(p (1 - p) (1 / nA + 1 / nB))`

and the two-sided p-value is `2 * (1 - Phi(|z|))` (`Phi` is the standard normal cdf, `scipy.stats.norm.cdf`).

Write `two_prop_test(kA, nA, kB, nB)` returning `(z, p_value)` as floats. If the standard error is zero (both groups have 0 or all
successes), return `(0.0, 1.0)`.

```python
two_prop_test(115, 1000, 100, 1000)        # z = 1.08, p = 0.28  (not significant)
```

## Example

Identical groups, `two_prop_test(50, 500, 50, 500)`, give `z = 0` and `p = 1`.
