## Approach

Chapter section 6. The number of trains in the station changes only at arrivals and departures, so walk through all those moments in time order and keep the count; the answer is its maximum. Which departure belongs to which train does not matter for the count, so the two lists can be sorted separately. Two indices merge the two sorted lists; on equal times the departure is taken first (the strict `<`), which is the chapter's same-time rule.

```python
def min_platforms(arrivals, departures):
    arr = sorted(arrivals)
    dep = sorted(departures)
    i = j = 0
    on_platform = best = 0
    while i < len(arr):
        if arr[i] < dep[j]:        # the next event is an arrival
            on_platform += 1
            best = max(best, on_platform)
            i += 1
        else:                      # a departure (also when the times are equal)
            on_platform -= 1
            j += 1
    return best
```

`dep[j]` never runs out while arrivals remain: every train leaves after it arrives, so by the time `j` departures are processed, more than `j` arrivals were.

Why this many platforms are also **enough**: it is the interval-partitioning argument of chapter section 6 (and p010 builds the actual assignment).

## Complexity

Two sorts, `O(n log n)`; the walk is `O(n)`. `O(n)` space for the sorted copies.

## Another way

Events: build `(time, +1)` for arrivals and `(time, -1)` for departures and sort them. Python sorts `(1000, -1)` before `(1000, 1)`, so departures come first on ties automatically. Then add them up in order and keep the maximum. Or the heap of chapter section 6: sort trains by arrival and keep a min-heap of departure times; reuse when `heap[0] <= arrival`.
