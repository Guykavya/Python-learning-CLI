## Approach

Sorting by start turns the schedule into a left-to-right walk. A gap appears exactly when the next meeting starts after everything seen so far has ended. The maximum of all gaps (including both ends) is the answer.

## Code

```python
t, n = map(int, input().split())
meetings = []
for _ in range(n):
    l, r = map(int, input().split())
    meetings.append((l, r))
meetings.sort()
busy_until = 0
best = 0
for l, r in meetings:
    best = max(best, l - busy_until)
    busy_until = max(busy_until, r)
best = max(best, t - busy_until)
print(best)
```

## Complexity

O(n log n) time for sorting, O(n) memory.

## Another way

Merge the intervals first (problem p018) and take the largest distance between consecutive merged blocks, plus both ends. The sweep above is the same thing without storing the merged list.
