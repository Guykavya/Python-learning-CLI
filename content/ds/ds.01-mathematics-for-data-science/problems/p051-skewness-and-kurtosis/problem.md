# Skewness and kurtosis

Chapter section 11.6. The **skewness** measures asymmetry: `m3 / m2^(3/2)` where `m_k = mean((x - mean)^k)`. The **excess kurtosis** measures heavy tails relative to a normal: `m4 / m2^2 - 3`. Both use the plain mean of the powers (divide by `n`, not `n - 1`).

Write `skewness(x)` and `excess_kurtosis(x)`. For a constant sample (`m2 = 0`) return `0.0` for both.

## Example

```text
skewness([1, 2, 3, 4, 5])            ->  0.0      (symmetric)
excess_kurtosis of a big normal sample -> about 0.0
skewness of an exponential sample    ->  about 2
```
