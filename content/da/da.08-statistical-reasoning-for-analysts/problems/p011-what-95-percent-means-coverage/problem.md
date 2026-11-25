# What "95 percent" means: coverage

Chapter section 4.3. "95% confidence" is a statement about the **procedure**: if you repeated the whole study many times, about 95
of every 100 intervals would contain the true value. You can check it by simulation when you know the truth.

Write `coverage(ci_fn, sampler, truth, reps, rng)`:

- `sampler(rng)` returns one new sample (a NumPy array) each time it is called;
- `ci_fn(sample)` returns `(low, high)`;
- repeat `reps` times (call `sampler(rng)` once per repetition, passing along the same `rng`) and return the **share** (between 0 and 1)
  of the intervals with `low <= truth <= high`.

```python
def sampler(rng):
    return rng.normal(10, 2, 30)

coverage(ci_mean, sampler, 10, 1000, np.random.default_rng(0))      # about 0.95
```

## Example

If `ci_fn` always returns `(0, 1)` and the truth is 0.5, coverage is 1.0; if the truth is 5, coverage is 0.0.
