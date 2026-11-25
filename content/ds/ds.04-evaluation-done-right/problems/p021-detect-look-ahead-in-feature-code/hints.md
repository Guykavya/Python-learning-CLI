## Hint 1

What is the difference between the series you pass in the two calls? Which value of each result do you compare?

## Hint 2

```text
full = feature_fn(series).iloc[t]
cut = feature_fn(series.iloc[: t + 1]).iloc[t]
return not isclose(full, cut, equal_nan=True)
```
