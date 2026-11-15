## Approach

Counting replaces comparisons by indexing: the value itself is the position in the `count` array. One pass counts, one pass writes.

## Code

```python
n, k = map(int, input().split())
a = [int(x) for x in input().split()]
count = [0] * (k + 1)
for x in a:
    count[x] += 1
out = []
for v in range(k + 1):
    out.extend([v] * count[v])
print(" ".join(map(str, out)))
```

## Complexity

O(n + k) time and O(n + k) memory. It beats `O(n log n)` when `k` is about `n` or smaller; it is useless when `k` is huge (values up to 10^18 would need an impossible table).

## Another way

The stable version for records (problem p027) uses prefix sums of the counts to give each key its starting position, and is the building block of radix sort (problem p028).
