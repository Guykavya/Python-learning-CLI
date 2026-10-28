## Approach

A heap is a list arranged so that `heap[i] <= heap[2*i+1]` and `heap[i] <= heap[2*i+2]`. That is
weaker than sorted, which is why it is cheap to keep, but strong enough that `heap[0]` is always
the minimum.

- `heapq.nsmallest(k, iterable)` keeps a small heap of the best k seen so far and returns them
  sorted. `nlargest` is the same in the other direction. Both take `key=`, and both give ties in
  input order (they behave like `sorted(...)[:k]`, which is stable).
- `pop_k_smallest` shows the machinery: `heapify` is O(n), and each `heappop` removes the
  smallest and repairs the heap in O(log n). Because `heapify` changes its argument, work on a copy.

`key=lambda r: r[field]` matters for the dicts: if you build `(value, record)` tuples yourself,
two equal values make Python compare two dicts and raise `TypeError`.

## Code

```python
import heapq
from collections.abc import Iterable


def k_smallest(nums: Iterable[int], k: int) -> list[int]:
    if k <= 0:
        return []
    return heapq.nsmallest(k, nums)


def top_k_by(records: list[dict], k: int, field: str) -> list[dict]:
    if k <= 0:
        return []
    return heapq.nlargest(k, records, key=lambda record: record[field])


def pop_k_smallest(nums: list[int], k: int) -> list[int]:
    heap = list(nums)
    heapq.heapify(heap)
    result = []
    while heap and len(result) < k:
        result.append(heapq.heappop(heap))
    return result
```

## Complexity

`nsmallest`/`nlargest`: O(n log k) time, O(k) memory. `pop_k_smallest`: O(n + k log n) time,
O(n) memory for the copy.

## Another way

`sorted(nums)[:k]` is O(n log n) and perfectly fine for small inputs; the docs even say that for
k close to n, sorting is faster. For k = 1 use `min()` / `max()`. The heap functions win when n is
large and k is small, or when the input is a stream you cannot sort.
