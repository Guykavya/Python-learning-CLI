# When the bootstrap fails

Chapter section 15.4. The bootstrap is not magic: it works for smooth statistics (mean, median) and **fails for extremes** such as the **maximum**, because a resample can never contain a value larger than the largest one in your sample.

Write `boot_coverage(draw, n, stat, truth, reps, boot_reps, seed)`:

- create `rng = np.random.default_rng(seed)`;
- `reps` times: draw a sample `x = draw(rng, n)` (1-D array of `n` values), compute a percentile bootstrap interval for `stat(x)` with `boot_reps` resamples and a 95% level (draw indices from the **same** `rng`), and check whether it contains `truth`;
- return the **fraction of intervals that contain `truth`**.

## Example

```text
median of Normal(0, 1) samples, n = 50, truth 0          ->  coverage near 0.95
maximum of Uniform(0, 1) samples, n = 50, truth 1        ->  coverage 0 (the interval always lies below 1)
```
