## Approach

Sort by start (chapter section 6). Keep the output as a list of `[start, end]` blocks. Each next interval either starts inside (or exactly at the end of) the last block, and extends it, or starts after it, and opens a new block. After sorting, a closed block can never grow again: every later interval starts at or after the current block's start, which is after the closed block's end. So each decision is final, which is what makes the greedy safe.

```python
def merge(intervals):
    out = []
    for s, e in sorted(intervals):
        if out and s <= out[-1][1]:             # overlaps or touches the current block
            out[-1][1] = max(out[-1][1], e)     # extend; max matters
        else:
            out.append([s, e])
    return out
```

`max` matters when an interval lies completely inside the current block, like `(2, 3)` inside `(1, 10)`. Building a new list `[s, e]` (and not reusing the input's inner list) keeps the caller's data unchanged.

## Complexity

`O(n log n)` for the sort, `O(n)` for the sweep, `O(n)` for the output.

## Another way

A sweep over events: turn each interval into `(s, +1)` and `(e, -1)`, sort with starts before ends at equal times (so touching intervals merge), and walk while counting how many are open; a block starts when the count goes from 0 to 1 and ends when it returns to 0. Longer, but the same idea answers "how many overlap at once" (p011).
