## Approach

Because the blocks are sorted and disjoint, they come in three runs. First, the blocks that end before `new` starts: they are untouched. Then the blocks that overlap or touch `new`: they all melt into one block, from the smallest start to the largest end. Then the blocks that start after `new` ends: untouched. One pass with an index handles the three runs in order.

```python
def insert_interval(intervals, new):
    ns, ne = new
    out = []
    i = 0
    n = len(intervals)
    while i < n and intervals[i][1] < ns:          # 1) ends before new starts: copy
        out.append([intervals[i][0], intervals[i][1]])
        i += 1
    while i < n and intervals[i][0] <= ne:         # 2) overlaps or touches new: absorb
        ns = min(ns, intervals[i][0])
        ne = max(ne, intervals[i][1])
        i += 1
    out.append([ns, ne])
    while i < n:                                   # 3) starts after new ends: copy
        out.append([intervals[i][0], intervals[i][1]])
        i += 1
    return out
```

The comparisons decide the touching rule: `end < ns` (strict) keeps a block that ends exactly at `ns` out of the first run, so the second run absorbs it; `start <= ne` absorbs a block that starts exactly at `ne`.

## Complexity

`O(n)` time, one pass. `O(n)` for the new list.

## Another way

`return merge(intervals + [new])` with the merge of p007: three lines and obviously correct, but `O(n log n)`. A useful **checker** for your fast version (the test uses it), and a fine answer when `n` is small. You could also find the first and last affected block with binary search (`bisect`, dsa.06), but copying the list is `O(n)` anyway.
