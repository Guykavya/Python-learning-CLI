# Draw many samples

Chapter section 2. Draw a sample, compute its mean, repeat many times: the means form the **sampling distribution** of the mean.
Its centre is the population mean, and its spread is `sigma / sqrt(n)`.

Write `sample_means(pop, n, reps, rng)`:

- `pop` is a NumPy array (the population), `n` the sample size, `reps` the number of samples,
  `rng` a `numpy.random.Generator` (`np.random.default_rng(seed)`);
- each sample is `n` values drawn from `pop` **without replacement** (`rng.choice(pop, n, replace=False)`);
- return a NumPy array of the `reps` sample means.

Use **only** the `rng` you are given. Never call `np.random.seed` or the global `np.random.*` functions: with the same seed the
function must return exactly the same numbers.

```python
rng = np.random.default_rng(1)
pop = rng.exponential(100, 20_000)
means = sample_means(pop, 50, 2000, np.random.default_rng(2))
print(means.mean(), pop.mean())          # close
print(means.std(), pop.std() / 50 ** .5) # close
```

## Example

`sample_means(np.arange(10.0), 10, 3, rng)` draws all ten values three times, so every mean is 4.5.
