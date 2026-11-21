## Approach

Write the formula of section 1.1 as code, one line per quantity, and compare with a strict `>`.

```python
def worth_it(minutes_per_run, runs_per_year, minutes_to_build, minutes_to_maintain_per_year, years=3):
    if min(minutes_per_run, runs_per_year, minutes_to_build, minutes_to_maintain_per_year) < 0 or years < 1:
        raise ValueError("times and counts must not be negative, and years must be at least 1")
    saved = minutes_per_run * runs_per_year * years
    cost = minutes_to_build + minutes_to_maintain_per_year * years
    return saved > 2 * cost, saved
```

Why maintenance is multiplied by the years: a script is not finished when it first works. Every year something around it changes, and the time to repair it is part of the price.

## Complexity

O(1): a few multiplications.

## Another way

Return the break-even point instead: `runs_needed = 2 * cost / (minutes_per_run * years)` tells you how many runs per year the task would need before it pays off. That number is often more convincing in a discussion than a plain yes or no.
