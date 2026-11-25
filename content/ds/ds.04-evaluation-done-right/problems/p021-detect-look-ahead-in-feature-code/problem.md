# Detect look-ahead in feature code

Chapter section 7.4. A time feature must use only values **up to** the prediction time. A cheap automatic test: compute the feature on the full series and on the series **cut at time `t`**; if the value at `t` changes when the future is deleted, the feature looks ahead.

Write `uses_future(feature_fn, series, t)` returning `True` if the feature looks ahead at position `t`:

- `feature_fn` takes a `pandas.Series` and returns a Series of the same length
- compare `feature_fn(series).iloc[t]` with `feature_fn(series.iloc[: t + 1]).iloc[t]`
- treat two `NaN` values as equal, and use `np.isclose` for the comparison
- return a plain `bool`

## Example

```text
uses_future(lambda x: x.shift(1).rolling(7).mean(), sales, 400)     ->  False
uses_future(lambda x: x.rolling(3, center=True).mean(), sales, 400) ->  True    (uses tomorrow)
uses_future(lambda x: x - x.mean(), sales, 400)                     ->  True    (the mean of the whole series)
```
