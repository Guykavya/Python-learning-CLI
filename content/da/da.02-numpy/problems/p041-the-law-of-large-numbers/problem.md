# The law of large numbers

Chapter sections 13.7 and 10.5. Write `running_mean_of_flips(n, rng)`: flip a fair coin `n` times with the Generator `rng` (1 = heads, 0 = tails), and return the **running proportion of heads**: element `i` is the mean of the first `i + 1` flips.

- Return a `float64` array of length `n` (`n = 0` gives an empty array). No Python loop.
- The first element is the first flip itself, so it is exactly `0.0` or `1.0`.
- For large `n` the last element is close to 0.5: that is the law of large numbers. The test checks `n = 100,000` on three seeds: the last value must be within 0.02 of 0.5 (the typical distance is about 0.0016).
- Use only the `rng` you are given; the same seed gives the same array.

## Example

```python
r = running_mean_of_flips(5, np.random.default_rng(0))
# if the flips were 1, 0, 0, 1, 1, the result would be
# array([1.        , 0.5       , 0.33333333, 0.5       , 0.6       ])
```
