## Approach

Think of events on a time line: `+1` at each start, `-1` at each end. Process the events in time order, ends before starts at the same time, and record the maximum running total.

## Code

```python
n = int(input())
starts = []
ends = []
for _ in range(n):
    s, e = map(int, input().split())
    starts.append(s)
    ends.append(e)
starts.sort()
ends.sort()
j = 0
best = 0
for i, s in enumerate(starts):
    while ends[j] <= s:
        j += 1
    best = max(best, i + 1 - j)
print(best)
```

## Complexity

O(n log n) time for the two sorts, O(n) memory.

## Another way

A min-heap of end times (LeetCode 253's usual solution): sort meetings by start, pop the earliest end if it is `<=` the next start, push the new end; the heap size at the end is the answer. A difference array works when times are small.
