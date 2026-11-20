## Approach

```python
def shrink(case, fails):
    case = list(case)
    if not fails(case):
        raise ValueError("the case does not fail")
    changed = True
    while changed:
        changed = False
        i = 0
        while i < len(case):
            candidate = case[:i] + case[i + 1:]
            if fails(candidate):
                case = candidate
                changed = True
            else:
                i += 1
    return case
```

When the loop ends, a full pass tried to remove each element and none could go, so the result is 1-minimal. The input list is copied first, so the caller's list is untouched.

Example: `[5, 7, 1, 9, 3, 3, 8]` with the predicate "a 7 comes before a 3". The first pass removes `5` (still fails), keeps `7`, removes `1` and `9`, removes the first `3` (another `3` is still there), keeps the second `3` and removes `8`. The result is `[7, 3]`.

## Complexity

Each pass makes at most `len(case)` calls to `fails` and removes at least one element or stops, so at most `n + 1` passes: `O(n^2)` calls in the worst case. Typical failures shrink in a pass or two.

## Another way

*Delta debugging* removes big chunks first (half, then quarters, ...) and needs far fewer calls for a long input with a tiny cause: `O(n log n)` instead of `O(n^2)`.
