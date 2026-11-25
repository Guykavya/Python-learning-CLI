## Approach

Each bug has a symptom and a one-line cause. `list.sort()` works in place (the mutation trap of Ch. 3.4); `sorted()` returns a new list. Dividing by `n` is the population formula. For an even count the two middle items are at `n // 2 - 1` and `n // 2`; the buggy code read one place too far to the right.

## Code

```python
import math


def summarise(values):
    if not values:
        raise ValueError("empty list")
    ordered = sorted(values)
    n = len(ordered)
    mean = sum(ordered) / n
    if n % 2:
        median = ordered[n // 2]
    else:
        median = (ordered[n // 2 - 1] + ordered[n // 2]) / 2
    if n < 2:
        sd = None
    else:
        sd = math.sqrt(sum((x - mean) ** 2 for x in ordered) / (n - 1))
    return {
        "n": n,
        "mean": mean,
        "median": median,
        "sd": sd,
        "min": ordered[0],
        "max": ordered[-1],
    }

```

## Complexity

O(n log n) for the sort.

## Another way

`statistics.median` and `statistics.stdev` give the same numbers; the exercise is to see why the hand-written version differed. A good habit is a test per bug that stays in the suite (the tests of this problem do that).
