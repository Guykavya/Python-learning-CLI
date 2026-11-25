# Build `describe()` and its report

This is the project slice of chapters 17 and 19: a reusable `describe()` and a text `report()` built on it. Write both.

## `describe(values)`

`values` is a list of numbers that may contain `None` (missing). Ignore the `None`s and return a dict with these keys:

| key | meaning |
|---|---|
| `n` | number of non-missing values |
| `missing` | number of `None`s |
| `mean`, `median` | the usual |
| `sd` | the **sample** standard deviation; `None` when `n == 1` |
| `min`, `max` | extremes |
| `q1`, `q3` | the quartiles with the **inclusive** method (when `n == 1`, both equal the value) |
| `iqr` | `q3 - q1` |
| `skew_hint` | `(mean - median) / pstdev` (the population sd), or `0.0` when the spread is 0 |

If nothing is left after removing `None`, raise `ValueError`. Do not change the input list.

## `report(name, values, unit="")`

Return **one string** of six lines, joined by `"\n"`:

```text
Response time  (n = 5, missing = 1)
----------------------------------------
centre : mean 34.0 ms   median 20.0 ms
spread : sd 37.3   IQR 10.0
range  : 10.0 to 100.0
advice : report the median (the mean and the median differ by more than 10%)
```

- line 1: `f"{name}  (n = {n}, missing = {missing})"` (two spaces before the bracket);
- line 2: 40 dashes;
- line 3: `centre : mean {mean:.1f}{u}   median {median:.1f}{u}` where `u` is `" " + unit` when the unit is not empty and `""` otherwise (three spaces between the two parts);
- line 4: `spread : sd {sd:.1f}   IQR {iqr:.1f}` (`n/a` instead of the sd number when `sd` is `None`);
- line 5: `range  : {min:.1f} to {max:.1f}`;
- line 6: `advice : ` followed by `report the median (the mean and the median differ by more than 10%)` when `abs(mean - median) > 0.10 * abs(median)` (the rule of chapter 10.6), else `either centre is fine`.

The example above is for the data `[10, 15, 20, 25, 100, None]`.
