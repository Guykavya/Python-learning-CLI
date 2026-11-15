## Approach

Backtracking over "pick the next candidate", where the pick may repeat the current candidate (`go(i, ...)`) but never go back to an earlier one. That makes every combination appear once, in sorted order. After sorting, the first candidate that is too big ends the loop (`break`): all later ones are bigger too.

## Code

```python
def combination_sum(candidates, target):
    candidates = sorted(candidates)
    result, path = [], []

    def go(start, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break
            path.append(c)
            go(i, remaining - c)      # i: the same number may be reused
            path.pop()

    go(0, target)
    return result
```

## Complexity

Exponential in `target / min(candidates)` (the maximum depth). The pruning keeps the tree small for the given limits.

## Another way

Decide, for each candidate in turn, **how many times** to use it (0, 1, 2, ... while it fits), then move to the next candidate. It produces the same combinations.
