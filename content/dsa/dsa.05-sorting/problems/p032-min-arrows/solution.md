## Approach

Greedy on the earliest right end: the arrow at the smallest `xe` bursts that balloon and every balloon starting at or before it; skip those, repeat.

## Code

```python
n = int(input())
balloons = []
for _ in range(n):
    xs, xe = map(int, input().split())
    balloons.append((xs, xe))
balloons.sort(key=lambda b: b[1])
arrows = 0
last = -10**18
for xs, xe in balloons:
    if xs > last:
        arrows += 1
        last = xe
print(arrows)
```

## Complexity

O(n log n) for the sort, O(n) for the sweep.

## Another way

Sort by start and keep the minimum end of the current group: the group ends when the next start exceeds that minimum. It is the same problem as 'partition intervals into the fewest groups that all share a point', and as 'maximum set of pairwise disjoint intervals' (problem p033).
