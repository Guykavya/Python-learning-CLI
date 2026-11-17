## Approach

One list, two repair moves. A new item goes to the end and **sifts up**. A pop takes the root, moves the **last** item into the root and **sifts down**. The constructor turns an arbitrary list into a heap with one `sift_down` per parent, from the last parent to the root (the items of the second half are leaves and are already one-item heaps). That costs less than `2n` comparisons, because a `sift_down` costs at most the height of its node, and most nodes are low.

## Code

```python
class MinHeap:
    def __init__(self, items=()):
        self._data = list(items)
        n = len(self._data)
        for i in range(n // 2 - 1, -1, -1):
            self._sift_down(i)

    def _sift_up(self, i):
        a = self._data
        while i > 0:
            p = (i - 1) // 2
            if a[i] < a[p]:
                a[i], a[p] = a[p], a[i]
                i = p
            else:
                break

    def _sift_down(self, i):
        a = self._data
        n = len(a)
        while True:
            smallest = i
            l, r = 2 * i + 1, 2 * i + 2
            if l < n and a[l] < a[smallest]:
                smallest = l
            if r < n and a[r] < a[smallest]:
                smallest = r
            if smallest == i:
                break
            a[i], a[smallest] = a[smallest], a[i]
            i = smallest

    def push(self, x):
        self._data.append(x)
        self._sift_up(len(self._data) - 1)

    def pop(self):
        if not self._data:
            raise IndexError("pop from an empty heap")
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            self._sift_down(0)
        return top

    def peek(self):
        if not self._data:
            raise IndexError("peek at an empty heap")
        return self._data[0]

    def __len__(self):
        return len(self._data)
```

## Complexity

`push` and `pop`: `O(log n)`. `peek` and `len`: `O(1)`. The constructor: `O(n)`. Memory: `O(n)`.

## Another way

`pop` can be written with the "hole" idea: move the hole down to a leaf along the smaller children, put the last item there and sift it up (this is what `heapq` does; it needs fewer comparisons). The constructor could also call `push` for each item: it is correct and `O(n log n)` in the worst case, which is exactly what the comparison test in this problem rejects.
