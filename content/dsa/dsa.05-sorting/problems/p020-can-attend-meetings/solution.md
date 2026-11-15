## Approach

Sort by start time. If any meeting begins before the previous meeting ends, two meetings overlap. Otherwise all fit.

## Code

```python
n = int(input())
meetings = []
for _ in range(n):
    s, e = map(int, input().split())
    meetings.append((s, e))
meetings.sort()
ok = True
for i in range(1, n):
    if meetings[i][0] < meetings[i - 1][1]:
        ok = False
        break
print("YES" if ok else "NO")
```

## Complexity

O(n log n) time, O(n) memory.

## Another way

Sort only the start times and the end times separately and compare `starts[i]` with `ends[i-1]` (the idea behind problem p031). Or sort the meetings by end time; the same test works there.
