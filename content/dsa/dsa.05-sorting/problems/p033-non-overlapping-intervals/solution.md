## Approach

Activity selection: sort by right end and take every interval compatible with the last taken one. An exchange argument shows that choosing the earliest-ending interval never hurts.

## Code

```python
n = int(input())
intervals = []
for _ in range(n):
    l, r = map(int, input().split())
    intervals.append((l, r))
intervals.sort(key=lambda x: x[1])
kept = 0
last_end = -10**18
for l, r in intervals:
    if l >= last_end:
        kept += 1
        last_end = r
print(n - kept)
```

## Complexity

O(n log n) for the sort, O(n) memory.

## Another way

Sort by start and, when two overlap, remove the one with the larger end (keep the one that ends first). It gives the same count and is how LeetCode 435's other solution is written. A dynamic programming solution works too, in O(n log n) with binary search.
