## Approach

```python
def first_bad(commits, is_bad):
    lo = 0                     # known good
    hi = len(commits) - 1      # known bad
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if is_bad(commits[mid]):
            hi = mid
        else:
            lo = mid
    return commits[hi]
```

The invariant: `commits[lo]` is good and `commits[hi]` is bad. Each test halves the gap between them. When the gap is 1, `hi` is the first bad commit: its predecessor is good.

Example with 8 commits (bad from `c5`): `lo = 0`, `hi = 7`; `mid = 3` (`c3`) is good, so `lo = 3`; `mid = 5` (`c5`) is bad, so `hi = 5`; `mid = 4` (`c4`) is good, so `lo = 4`. The gap is 1: the answer is `c5`, after 3 tests instead of 6.

## Complexity

`O(log n)` calls to `is_bad`; the cost of the tests dominates.

## Another way

`git bisect run ./test.sh` does this loop for you, using the exit code of your script (0 = good, 1 to 127 = bad, 125 = skip). With 1,000 commits you need at most 10 tests.

## Why it matters

When a regression appears and you do not know where it came from, 10 tests are better than 1,000. This works only when each commit is testable (see p007).
