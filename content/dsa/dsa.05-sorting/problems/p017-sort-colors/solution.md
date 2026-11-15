## Approach

Because the value range is tiny, counting gives an `O(n)` sort. The Dutch flag does the same in place with one pass and three zones: `[0..lo)` zeros, `[lo..i)` ones, `(hi..n)` twos.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
count = [0, 0, 0]
for x in a:
    count[x] += 1
out = []
for v in range(3):
    out.extend([v] * count[v])
print(" ".join(map(str, out)))
```

## Complexity

O(n) time. Counting uses O(1) extra space apart from the output.

## Another way

Counting sort in general (problem p026) handles any small range of values; this problem is its smallest case. Three-way quick sort (problem p037) uses the same Dutch flag partition with a pivot value in the middle zone.
