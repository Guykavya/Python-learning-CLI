## Hint 1

Every statistic has a pandas method (section 16.1 and 16.3): `mean()`, `median()`, `std()`, `quantile(0.25)`, `skew()`. They skip missing values already. What do they return when there is nothing, or too little, to compute (a `NaN`)? And what must `n` count?

## Hint 2

```text
x = s.dropna()
n = len(x)
if n == 0: return the dict with None everywhere (n 0, missing len(s))
return {"n": n, "missing": len(s) - n,
        "mean": x.mean(), "median": x.median(), "sd": x.std(),
        "q1": x.quantile(0.25), "q3": x.quantile(0.75), "skew": x.skew()}
```
Convert each number with a helper that turns `NaN` into `None` and everything else into a plain `float`.
