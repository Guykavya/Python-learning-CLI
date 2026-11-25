# Three percentiles by hand

Chapter section 12.2. The same data and the same `p` give **different** percentiles under different definitions:

- **nearest-rank**: the smallest value with at least `p` percent of the data at or below it (rank = `ceil(p / 100 * n)`, at least 1);
- **inclusive**: linear interpolation at 0-based position `(n - 1) * p / 100` (the minimum is the 0th percentile, the maximum the 100th);
- **exclusive**: linear interpolation at 1-based position `(n + 1) * p / 100`; it refuses a `p` whose position falls outside `1 ... n`.

```python
import math


def percentile_nearest_rank(values, p):
    ordered = sorted(values)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def percentile_inclusive(values, p):
    ordered = sorted(values)
    position = (len(ordered) - 1) * p / 100
    low = math.floor(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] + (ordered[high] - ordered[low]) * fraction


def percentile_exclusive(values, p):
    ordered = sorted(values)
    n = len(ordered)
    position = (n + 1) * p / 100
    if position < 1 or position > n:
        raise ValueError(f"p={p} is too extreme for {n} values with the exclusive method")
    low = math.floor(position)
    high = min(low + 1, n)
    fraction = position - low
    return ordered[low - 1] + (ordered[high - 1] - ordered[low - 1]) * fraction


data = [15, 20, 35, 40, 50]
for p in (25, 50, 90):
    print(f"p={p}")
    print(f"  nearest-rank: {percentile_nearest_rank(data, p):.2f}")
    print(f"  inclusive:    {percentile_inclusive(data, p):.2f}")
    try:
        print(f"  exclusive:    {percentile_exclusive(data, p):.2f}")
    except ValueError as error:
        print(f"  exclusive:    {error}")
```

Hand-trace the program and write all **12 printed lines** in `answer.txt` (two decimals, and the exact text of the error message if there is one).

For a check afterwards, the library gives `statistics.quantiles([15, 20, 35, 40, 50], n=4)` = `[17.5, 35.0, 45.0]` (exclusive, the default) and `method="inclusive"` = `[20.0, 35.0, 40.0]`.

## Answer format

For each of the three values of `p`: the line `p=...`, then three indented lines, so 12 lines.

## After you answer

- At `p=25` the three methods give three different numbers. Which one never returns a value that is not in the data?
- Why does the exclusive method refuse `p=90` on 5 values, and what does the library do instead?
