# Power by simulation

Chapter section 5.5. The **power** of a test is the probability that it detects a real effect of a given size. Simulate it: generate many
experiments in which the true rates are `p0` and `p1`, test each one, and count how often the test says "significant" at 0.05.

Write `power(p0, p1, n, sims, rng)`:

- each simulated experiment draws `ka ~ Binomial(n, p0)` and `kb ~ Binomial(n, p1)` (use `rng.binomial(n, p, sims)` for all `sims` at once);
- the test is the pooled two-proportion z-test of problem 18: `pp = (ka + kb) / (2 n)`, `z = (kb - ka) / n / sqrt(pp (1 - pp) (2 / n))`,
  two-sided p-value `< 0.05` means a detection;
- return the share of the `sims` experiments with a detection.

Use only `rng`. Handle `pp = 0` or `pp = 1` (SE zero): such an experiment is **not** a detection.

```python
power(0.10, 0.115, 4000, 2000, np.random.default_rng(1))      # about 0.58
power(0.10, 0.10, 1000, 2000, np.random.default_rng(1))       # about 0.05: the false alarm rate
```

## Example

With no real effect (`p1 = p0`) the "power" is just the false alarm rate, close to 0.05.
