# Fix the summary function

A teammate wrote `summarise(values)` for a report. It runs, it returns numbers, and it has **three bugs**. Your job: find them from the symptoms, fix them, and keep everything else the same. The file `solution.py` already contains this code; edit it.

```python
import math


def summarise(values):
    """Return n, mean, median, sd (sample), min and max of a list of numbers."""
    if not values:
        raise ValueError("empty list")
    values.sort()
    n = len(values)
    mean = sum(values) / n
    if n % 2:
        median = values[n // 2]
    else:
        median = (values[n // 2] + values[n // 2 + 1]) / 2
    variance = sum((x - mean) ** 2 for x in values) / n
    return {
        "n": n,
        "mean": mean,
        "median": median,
        "sd": math.sqrt(variance),
        "min": values[0],
        "max": values[-1],
    }
```

Required behaviour:

- the returned dict has exactly the keys `n, mean, median, sd, min, max`;
- `sd` is the **sample** standard deviation (divide by `n - 1`), and `None` for a single value;
- `median` is the middle value, or the mean of the two middle values for an even count;
- the caller's list is **never changed**;
- an empty list raises `ValueError`.

## Symptoms the teammate reported

1. "After I call `summarise(marks)` my `marks` list is suddenly sorted."
2. "My `sd` is smaller than `statistics.stdev` gives."
3. "`summarise([1, 2])` crashes, and for `[1, 2, 3, 4]` the median is wrong."

## Example

```python
summarise([4, 1, 3, 2])
# {'n': 4, 'mean': 2.5, 'median': 2.5, 'sd': 1.2909..., 'min': 1, 'max': 4}
```
