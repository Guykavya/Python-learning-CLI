# Normal cdf and inverse

Chapter section 11.5. The normal **cdf** `P(X <= x)` has no formula in elementary functions, but `math.erf` gives it: `0.5 * (1 + erf((x - mu) / (sigma * sqrt(2))))`. The inverse, the **quantile function** (`ppf`), answers "which `x` has probability `q` below it?". You can find it by **bisection** because the cdf is increasing.

Write `normal_cdf(x, mu=0.0, sigma=1.0)` and `normal_ppf(q, mu=0.0, sigma=1.0)`. `normal_ppf` must raise `ValueError` unless `0 < q < 1`. Do not import SciPy.

## Example

```text
normal_cdf(0)        ->  0.5
normal_cdf(1.96)     ->  0.9750
normal_ppf(0.975)    ->  1.95996
```
