# Capacity to ship packages

Packages with weights `w[0], w[1], ..., w[n-1]` must be shipped **in this order** (you cannot reorder them). Each day a ship loads packages from the front of the remaining line, one after another, as long as the total weight does not exceed the ship's capacity `C`. The next day it continues with the first package that did not fit.
All packages must be shipped within `D` days. Print the **smallest capacity `C`** that works.

The capacity must be at least `max(w)` (otherwise the heaviest package never ships). With capacity `C`, count the days greedily: keep adding packages to today's load; when the next one does not fit, start a new day.
More capacity never needs more days, so "days needed at capacity `C` is `<= D`" is False...False True...True.

## Input

- Line 1: `n D`.
- Line 2: `n` weights.

## Output

One integer: the minimum capacity.

## Constraints

- `1 <= D <= n <= 100000`
- `1 <= w[i] <= 10^9`

## Example

Input:

```
6 3
3 2 2 4 1 4
```

Output:

```
6
```

(Capacity 6: day 1 carries `3 + 2`, day 2 carries `2 + 4`, day 3 carries `1 + 4`. Capacity 5 needs 4 days: `3 + 2`, `2`, `4 + 1`, `4`.)
