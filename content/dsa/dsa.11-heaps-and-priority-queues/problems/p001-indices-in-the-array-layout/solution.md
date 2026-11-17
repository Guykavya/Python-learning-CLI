## Approach

The tree is complete, so the items of each level sit next to each other in the list. Level `d` starts at index `2**d - 1`. Counting how many nodes come before a node gives the formulas: the node at index `i` has its children at `2*i + 1` and `2*i + 2`, and the parent of a node is found by undoing it: `(i - 1) // 2`. `children` just filters the two child indexes with `c < n`.

## Code

```python
def parent(i):
    return (i - 1) // 2


def left(i):
    return 2 * i + 1


def right(i):
    return 2 * i + 2


def children(i, n):
    return [c for c in (left(i), right(i)) if c < n]
```

## Complexity

`O(1)` for every function.

## Another way

Some books number the array from **1**: then `left(i) = 2*i`, `right(i) = 2*i + 1` and `parent(i) = i // 2`. Both numberings describe the same tree; they differ only by a shift of one. This course (and Python's `heapq`) uses index 0, so keep `2*i + 1`. A leaf is any index `i` with `left(i) >= n`, that is `i >= n // 2`: that is why heapify starts at `n // 2 - 1`, the last parent.
