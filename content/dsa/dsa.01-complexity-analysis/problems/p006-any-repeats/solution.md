## Approach

Walk through the numbers once and keep a set of everything seen so far. If the current number is already in
the set, there is a repeat. A set looks up a value by its hash, so `x in seen` and `seen.add(x)` take O(1) time
on average, independent of the set's size.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

seen = set()
found = False
for x in a:
    if x in seen:
        found = True
        break
    seen.add(x)
if found:
    print("YES")
else:
    print("NO")
```

## Complexity

- Time: O(n) on average: one pass, O(1) work per number. The starter was O(n^2).
- Space: O(n) for the set. We traded memory for time, which is the most common trade in this course.

On this machine, 200000 numbers take about 0.05 seconds with the set. The starter would need roughly
2 * 10^10 comparisons: tens of minutes.

## Another way

- One line: `len(set(a)) < n`. A set keeps one copy of each value, so it is smaller than the list exactly when
  something repeated. Also O(n), but it cannot stop early.
- Sort first, then compare neighbours: after `a.sort()`, equal values sit next to each other, so check
  `a[i] == a[i + 1]` for each `i`. That is O(n log n) time and needs no extra set. Useful when memory is tight.
