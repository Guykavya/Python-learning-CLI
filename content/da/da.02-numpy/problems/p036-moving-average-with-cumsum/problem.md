# Moving average with `cumsum`

Chapter section 12.1 (example 3) and 10.5. Write `moving_average(x, k)`: the mean of every window of `k` consecutive values of the 1-D array (or list) `x`, from the window that starts at position 0 to the one that ends at the last value.

- The result is a `float64` array of length `len(x) - k + 1`; element `i` is `mean(x[i : i + k])`.
- `k` must satisfy `1 <= k <= len(x)`; otherwise raise `ValueError` with a message that names `k` and `len(x)`.
- Use the running-total trick: the sum of a window is the difference of two running totals. Its cost does not depend on `k`. The test runs `n = 1,000,000` and `k = 200,000` in a subprocess with a time limit of 8 seconds; summing every window again (a loop, `np.convolve`, or `sliding_window_view(...).mean(...)`) does `n × k` work and runs out of time. The running-total version needs a few milliseconds.
- Do not change the caller's array.

## Example

```python
moving_average([2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 8.0], 3)
# array([ 4.,  6.,  8., 10., 10.])
moving_average([1, 2, 3, 4], 4)
# array([2.5])
moving_average([1, 2, 3], 5)
# ValueError: window k=5 must be between 1 and len(x)=3
```
