## Approach

The grid of all sums has sorted rows and sorted columns. So the next smallest pair is always **next to** a pair that is already taken: it is the right neighbour of a taken cell, or the first cell of a row that is not started yet. We never build the grid. We keep a heap of the cells that could come next and generate only as many as we need: `O(k)` cells for `k` answers.

- Start with the first column of the first `min(k, len(a))` rows (the other rows cannot reach the top `k`: the first cell of row `k` has `k` cells above it with a sum that is smaller or equal).
- Pop the smallest cell, output the pair, push the right neighbour of that cell.

Each entry is `(sum, i, j)`: two cells with the same sum are told apart by `i` and `j`, which are integers and always comparable.

## Code

```python
import heapq

def k_smallest_pairs(a, b, k):
    if not a or not b or k <= 0:
        return []
    heap = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]
    heapq.heapify(heap)
    result = []
    while heap and len(result) < k:
        _, i, j = heapq.heappop(heap)
        result.append((a[i], b[j]))
        if j + 1 < len(b):
            heapq.heappush(heap, (a[i] + b[j + 1], i, j + 1))
    return result
```

## Complexity

`O(min(k, len(a)) + k log k)` time, `O(min(k, len(a)))` memory for the heap besides the result. The pairs are generated **in order** and lazily: nothing about the cells that are never reached is computed.

## Another way

- A frontier with both neighbours: start with `(0, 0)` only; after popping `(i, j)` push `(i + 1, j)` and `(i, j + 1)`, with a `seen` set so that a cell is pushed once. Same cost, a bit more bookkeeping.
- Only the first `k` items of each list can be in the answer, so `heapq.nsmallest(k, product(a[:k], b[:k]), key=sum)` works too, but it looks at `k * k` pairs instead of `k`.
- Brute force: build all pairs and sort: `O(nm log nm)`. For `n = m = 100,000` that is 10 billion pairs: it does not fit in time or memory.
