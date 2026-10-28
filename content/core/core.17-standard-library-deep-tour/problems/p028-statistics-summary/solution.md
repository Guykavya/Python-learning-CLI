## Approach

Each statistic is one call. The decisions are about edge cases and about *which* formula:

- `median` sorts a copy for you, so the input order does not matter and the input is not changed.
- `multimode` returns all the most common values (a list), where `mode` returns only one.
- `stdev` is the sample standard deviation (divide by `n - 1`) and needs two values;
  `pstdev` is the population one (divide by `n`) and works with one value (it is 0).
- `quantiles(data, n=4)` returns the three cut points between four equal groups: Q1, Q2 (the
  median), Q3. With its default `method="exclusive"` the result for 1..8 is `[2.25, 4.5, 6.75]`.

The outlier rule uses those cut points: anything more than 1.5 times the middle spread below Q1
or above Q3 is unusual.

## Code

```python
import statistics


def summary(data: list[float]) -> dict[str, object]:
    if not data:
        raise ValueError("summary() needs at least one value")
    return {
        "count": len(data),
        "mean": statistics.fmean(data),
        "median": statistics.median(data),
        "modes": statistics.multimode(data),
        "stdev": statistics.stdev(data) if len(data) >= 2 else None,
        "pstdev": statistics.pstdev(data),
        "range": max(data) - min(data),
    }


def quartiles(data: list[float]) -> list[float]:
    return statistics.quantiles(data, n=4)


def outliers(data: list[float]) -> list[float]:
    q1, _, q3 = quartiles(data)
    spread = q3 - q1
    low, high = q1 - 1.5 * spread, q3 + 1.5 * spread
    return [x for x in data if x < low or x > high]
```

## Complexity

`median` and `quantiles` sort: O(n log n). The rest is O(n). The summary makes several passes
over the data; that is fine for anything that fits in memory.

## Another way

`statistics.mean` keeps exact types (the mean of `Fraction`s is a `Fraction`), while `fmean` always
converts to `float` and is faster. For data that is too large to keep, you would compute count,
mean and variance in one pass (Welford's method) instead of calling these functions.
