## Approach

Every item except the root has exactly one parent, at index `(i - 1) // 2`. The list is a min-heap exactly when no item is smaller than its parent. So one loop over `i = 1 .. n - 1` that compares `a[i]` with `a[(i - 1) // 2]` is enough. Empty and one-item lists have no pairs, so they are heaps.

## Code

```python
def is_min_heap(a):
    for i in range(1, len(a)):
        if a[i] < a[(i - 1) // 2]:
            return False
    return True
```

## Complexity

`O(n)` time, `O(1)` extra memory: each item is compared once, with its parent.

## Another way

Loop over the parents, `range(len(a) // 2)`, and test both children with an `if left < n` / `if right < n` guard. It does the same comparisons, in a different order, and needs more code. Do not check only neighbours (`a[i] <= a[i + 1]`): that tests for a **sorted** list, which is a much stronger condition than a heap.
