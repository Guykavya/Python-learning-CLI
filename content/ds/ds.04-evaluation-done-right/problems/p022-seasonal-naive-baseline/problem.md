# Seasonal-naive baseline

Chapter section 7.5. For a series with a weekly pattern, the baseline to beat is **seasonal naive**: "this Tuesday will be like last Tuesday". For a horizon of `h` steps after the end of the training series, step `i` (starting at 0) is forecast by the value one season earlier, repeating the last full season:

```text
forecast[i] = train[len(train) - season + (i % season)]
```

Write `seasonal_naive(train, horizon, season=7)` returning a float NumPy array of length `horizon`. If the training series is shorter than one season, raise `ValueError`.

<details><summary>The data generator <code>make_sales</code> (chapter section 7.2)</summary>

```python
def make_sales(n=730, seed=0):
    r = np.random.default_rng(seed)
    t = np.arange(n)
    dow = t % 7
    promo = (r.random(n) < 0.10).astype(int)
    noise = np.zeros(n)
    for i in range(1, n):                                  # noise that persists for a few days
        noise[i] = 0.6 * noise[i - 1] + r.normal(0, 6)
    y = 100 + 0.25 * t + 15 * np.sin(2 * np.pi * dow / 7) + 30 * promo + noise
    return pd.DataFrame({"day": t, "dow": dow, "promo": promo, "sales": y})
```
</details>

## Example

```text
seasonal_naive([1, 2, ..., 14], 10, 7)  ->  [8, 9, 10, 11, 12, 13, 14, 8, 9, 10]
```
