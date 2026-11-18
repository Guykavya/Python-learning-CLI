## Approach

Each letter occupies an interval from its first to its last occurrence; pieces may not cut through any of these intervals. Scanning from the left, the current piece must reach the largest "last occurrence" of every letter in it. The moment the scan reaches that point, cutting is allowed, and cutting at the **earliest** allowed point is always right: a later cut would only merge pieces, never allow more of them. (The same idea as merging overlapping intervals, chapter section 6.)

```python
def partition_labels(s):
    last = {ch: i for i, ch in enumerate(s)}      # the last index wins
    sizes = []
    start = 0
    end = 0
    for i, ch in enumerate(s):
        end = max(end, last[ch])
        if i == end:                               # no letter in the piece appears later
            sizes.append(i - start + 1)
            start = i + 1
    return sizes
```

Trace `"eccbbbbdec"`: `last` is `e: 8, c: 9, b: 6, d: 7`. At `i = 0` the end is 8; at `i = 1` it becomes 9 (the last `c`). It only reaches `i` at the very end: one piece of length 10.

## Complexity

Two passes over `s`: `O(n)` time. The dictionary has at most 26 keys: `O(1)` extra space (plus the output).

## Another way

Build the interval `[first, last]` of each letter, sort the intervals by start, and **merge** overlapping ones exactly as in "merge intervals" (chapter section 6). The merged intervals are the pieces; return their lengths. It is `O(n + 26 log 26)` and shows clearly why the problem is an interval problem in disguise.
