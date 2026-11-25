# Does the model beat seasonal naive?

Chapter sections 7.3 and 7.5. To claim a forecasting model is useful, compare it with seasonal naive on **several** forecast origins (a *rolling-origin backtest*).

Write `beats_seasonal_naive(model_fn, df, origins, horizon=28, season=7)`. `df` has the columns `day, dow, promo, sales` (as made by `make_sales`). For each `o` in `origins`:

- `train = df.iloc[:o]`, `future = df.iloc[o:o + horizon]`
- the model forecast is `model_fn(train, future.drop(columns="sales"))` (the model may use `day`, `dow` and the **planned** `promo` of the future days, never their sales)
- the baseline forecast is seasonal naive of `train["sales"]` (repeat the last `season` values, as in the previous problem)
- record the MAE of each against `future["sales"]`

Return `(model_mae, naive_mae, beats)`: the two MAEs **averaged over the origins** (floats) and `beats = model_mae < naive_mae` (a plain `bool`).

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
a linear model on day, day of week and promo   ->  (5.9, 13.3, True)
predicting the training mean                     ->  (71.1, 13.3, False)
```
