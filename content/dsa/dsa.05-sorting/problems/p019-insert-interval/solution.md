## Approach

Walk through the sorted list with one index and three phases: before, overlapping, after. The overlapping phase grows `[a, b]`.

## Code

```python
n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
a, b = map(int, input().split())
out = []
i = 0
while i < n and intervals[i][1] < a:
    out.append(intervals[i])
    i += 1
while i < n and intervals[i][0] <= b:
    a = min(a, intervals[i][0])
    b = max(b, intervals[i][1])
    i += 1
out.append((a, b))
while i < n:
    out.append(intervals[i])
    i += 1
for l, r in out:
    print(l, r)
```

## Complexity

O(n) time, O(n) memory for the output.

## Another way

Append the new interval to the list, sort, and run the merge-intervals sweep of problem p018. That is simpler but O(n log n). Binary search can find the first affected interval in O(log n), but copying the output is still O(n).
