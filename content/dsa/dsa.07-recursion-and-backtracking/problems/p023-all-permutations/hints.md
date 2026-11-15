## Hint 1

A permutation is complete when the path has `len(nums)` items. At each level, which items may be placed next?

## Hint 2

Keep `used = [False] * n`. Loop over all positions `i`; skip used ones; mark, append, recurse, then pop and unmark.

## Hint 3

```
def go():
    if len(path) == n: result.append(path[:]); return
    for i in range(n):
        if used[i]: continue
        used[i] = True; path.append(nums[i])
        go()
        path.pop(); used[i] = False
```
