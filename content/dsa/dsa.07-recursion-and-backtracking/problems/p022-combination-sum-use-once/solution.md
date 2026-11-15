## Approach

Combine two ideas from the chapter. `go(i + 1, ...)` makes each position usable once. Sorting plus the sibling skip rule (`i > start` and equal to the previous value) makes each **value** start a sub-tree at most once per level, so no combination is produced twice. The `break` on a too-large candidate is valid after sorting.

## Code

```python
def combination_sum2(candidates, target):
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
            if i > start and c == candidates[i - 1]:
                continue                     # duplicate sibling
            path.append(c)
            go(i + 1, remaining - c)         # each position once
            path.pop()

    go(0, target)
    return result
```

## Complexity

Exponential in the worst case, but the skip rule makes the tree as small as if each distinct value appeared with a count: for `[1] * 30`, target 15, the tree is a single chain of 16 calls.

## Another way

Count each distinct value (`collections.Counter`) and decide for each value how many copies (0 .. count) to take. That is the "multiset" view and gives the same answers.
