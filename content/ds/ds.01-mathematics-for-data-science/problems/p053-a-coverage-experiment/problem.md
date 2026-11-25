# A coverage experiment

Chapter section 13.4. A 95% confidence interval means: **in repeated experiments, about 95% of the intervals contain the true value.** You can check this by simulation. With small samples the **z-interval** (using 1.96 and the sample standard deviation) is too narrow, which is why the t-interval exists.

Write `coverage(ci_fn, n, reps, seed)`: using `rng = np.random.default_rng(seed)`, draw `reps` samples of size `n` from a **standard normal** (true mean 0), compute `ci_fn(sample)` (which returns `(low, high)`) for each, and return the **fraction of intervals that contain 0**.

## Example

```text
coverage(t_interval, n=5, reps=4000, seed=0)  ->  about 0.95
coverage(z_interval, n=5, reps=4000, seed=0)  ->  about 0.88   (too many misses)
```
