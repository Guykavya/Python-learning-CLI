**1. What it computes.** The **moving average** (rolling mean) of `xs` over windows of `k`
neighbouring values. Better names: `moving_average(values, window)`, with `r` = `averages`
and `w` = `window_sum`.

**2. How it works.** `w` starts as the sum of the first window, `xs[0:k]`. At the top of the
step for index `i`, `w` is the sum of the window `xs[i-k:i]` (the `k` values just **before**
`i`). The loop appends its average, then **slides** the window one place right: add the value
entering (`xs[i]`) and subtract the one leaving (`xs[i-k]`). That is O(1) per step instead of
O(k) for a fresh `sum`, so the whole function is O(n) instead of O(n·k).

**3. The bug.** For `[2, 4, 6, 8, 10]` and `k = 2` the windows are `[2,4] [4,6] [6,8] [8,10]`,
so the answer should be `[3.0, 5.0, 7.0, 9.0]`: **four** averages (`n - k + 1`). The last
window's sum is computed in the final step, but the loop ends before it is appended. Classic
off-by-one: it returns `n - k` items. Even worse, with `k = len(xs)` it returns `[]` instead of
the one overall average.

**4. Edge cases.** `k = 0`: `w / k` raises `ZeroDivisionError` (an average of zero values makes
no sense, so it should be a clear `ValueError`). `k > len(xs)`: the loop never runs and the
result is `[]`, which is reasonable (no full window exists) but should be documented. Negative
`k` gives nonsense slices.

**5. Fixed version.**

```python
def moving_average(values, window):
    """Average of each run of `window` neighbouring values (n - window + 1 results)."""
    if window <= 0:
        raise ValueError("window must be positive")
    if window > len(values):
        return []
    window_sum = sum(values[:window])
    averages = [window_sum / window]
    for i in range(window, len(values)):
        window_sum += values[i] - values[i - window]
        averages.append(window_sum / window)
    return averages
```

Then add tests for `k = 1`, `k = len`, `k = 0` and the example, so it stays fixed.
