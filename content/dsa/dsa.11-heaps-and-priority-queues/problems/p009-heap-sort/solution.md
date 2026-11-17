## Approach

Phase 1 turns the list into a heap in `O(n)`. Phase 2 does `n - 1` rounds. In every round the root (the largest item of the heap part for an ascending sort) is swapped to the end of the heap part, which is its final position, the heap part shrinks by one, and the new root, which is an arbitrary small item, sinks back down in `O(log n)`. The sorted part and the heap part share the one list, so no extra memory is needed. For the descending order, flip the comparison: a min-heap puts the smallest item last.

## Code

```python
def heap_sort(a, reverse=False):
    n = len(a)

    def sift_down(i, end):
        while True:
            top = i
            for c in (2 * i + 1, 2 * i + 2):
                if c < end and (a[c] < a[top] if reverse else a[top] < a[c]):
                    top = c
            if top == i:
                return
            a[i], a[top] = a[top], a[i]
            i = top

    for i in range(n // 2 - 1, -1, -1):      # phase 1: build the heap
        sift_down(i, n)
    for end in range(n - 1, 0, -1):          # phase 2: move the root behind the heap
        a[0], a[end] = a[end], a[0]
        sift_down(0, end)
```

## Complexity

`O(n log n)` time in every case (about `2 n log2 n` comparisons). `O(1)` extra memory. Not stable.

## Another way

Without the in-place requirement the simplest sort with a heap is "heapify a copy, pop `n` times" (`O(n log n)`, `O(n)` memory), which is what `heapq` makes easy. Selection sort also finds the largest item `n` times, but by scanning (`O(n)` each time), so it is `O(n^2)`: the heap makes "find the largest" cost `O(log n)` instead.
