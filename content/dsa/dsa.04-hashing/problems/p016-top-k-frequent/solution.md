## Approach

Count every value with a dictionary, then sort the **distinct** values by `(-count, value)`. The minus sign turns
"largest count first" into the natural ascending order of a sort key. Take the first `k`.

## Code

```python
n, k = map(int, input().split())
a = [int(x) for x in input().split()]

count = {}
for x in a:
    count[x] = count.get(x, 0) + 1

ranked = sorted(count, key=lambda v: (-count[v], v))
print(*ranked[:k])
```

## Complexity

O(n) to count, O(d log d) to sort `d` distinct values. Total O(n log n) worst case.

## Another way

**Bucket by count**: counts are at most `n`, so make a list of lists `bucket[c]` and read it from the top. That is O(n)
and avoids a sort. For `k` much smaller than `d` a heap (`heapq.nlargest`) is O(d log k).
