# Fix the biased sampler

Chapter section 3.1. A teammate wrote `draw(pop, n, rng)` to take a random sample of `n` customers from a table `pop` (one row per
customer, columns `customer_id`, `signup_day`, `spend`). It has two bugs:

```python
def draw(pop, n, rng):
    ordered = pop.sort_values("signup_day")
    sample = ordered.iloc[: n - 1]                  # the n - 1 oldest customers
    return pd.concat([sample, sample.iloc[[0]]])    # an off-by-one "fix" that repeats a row
```

1. The sample is **not random**: it takes the first rows of a table sorted by signup date, so it contains only the oldest customers
   (who spend differently from newer ones).
2. It returns `n` rows, but one customer appears **twice**.

Fix `draw` in `solution.py`: return exactly `n` **distinct** rows of `pop`, chosen at random **using the `rng` you are given**
(`numpy.random.Generator`), with the same columns. The same seed must give the same sample; different seeds different samples.

## Example

With 5,000 customers whose spend falls with signup day, the buggy sampler's mean spend is far above the population mean; a
random sample's mean is close to it, on average.
