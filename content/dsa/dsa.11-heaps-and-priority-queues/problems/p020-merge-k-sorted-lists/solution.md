## Approach

Every inner list is sorted, so the overall minimum is among the **first** items of the lists. Keep a min-heap with the current front item of each non-empty list. Pop the smallest, add it to the result, and push the next item of the **same** list (if it has one). The heap never holds more than `k` items, so every step costs `O(log k)`.

An entry is `(value, list_number, position)`. The second field breaks ties between equal values (equal front items of different lists), so the heap never has to compare anything else.

## Code

```python
import heapq

def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    result = []
    while heap:
        value, i, j = heapq.heappop(heap)
        result.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return result
```

## Complexity

`O(N log k)` time for `N` numbers in total and `k` lists; the heap holds at most `k` entries, so the extra memory is `O(k)` besides the result.

## Another way

- `heapq.merge(*lists)` does exactly this (lazily, as an iterator): the standard library version of the same algorithm.
- Merge **two lists at a time**, like merge sort: `k` lists need `log k` rounds, each round touches all `N` numbers, so the time is `O(N log k)` too, without a heap.
- Concatenate and sort: `O(N log N)`. Python's sort recognises the sorted runs and is fast in practice, but it needs `O(N)` extra memory and does not work when the lists are streams that you cannot hold in memory.
- The lazy variant: make the function a generator (`yield value` instead of `append`). The first numbers appear without reading the rest of any list.
