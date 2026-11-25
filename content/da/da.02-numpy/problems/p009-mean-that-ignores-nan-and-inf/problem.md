# Mean that ignores nan and inf

Chapter sections 4.6, 8.5 and 10.4. Sensor data contains `nan` (missing) and `inf` (a broken division upstream).
Write `clean_mean(x)` that returns a tuple `(mean, n_dropped)`:

- `mean` is the mean of the **finite** values of `x` (any shape), as a float;
- `n_dropped` is how many values were left out (`nan`, `inf` and `-inf`), as an int;
- if no finite value is left (all bad, or `x` is empty), return `(nan, n_dropped)` **without a RuntimeWarning**.
  The tests turn warnings into errors, so `np.mean` of an empty array or `np.nanmean` of an all-`nan` array fails.

## Example

```python
clean_mean(np.array([1.0, np.nan, 3.0, np.inf]))   # (2.0, 2)
clean_mean(np.array([np.nan, -np.inf]))            # (nan, 2)
clean_mean(np.array([]))                           # (nan, 0)
```
