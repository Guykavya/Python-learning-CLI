## Approach

This is two-sum, but counting instead of stopping at the first pair. Walk from left to right. Before adding `x` to the table,
every earlier element equal to `k - x` forms a pair with it, and the table says how many there are. Adding `x` **after** the
lookup means an element can never pair with itself.

## Code

```python
n, k = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {}
answer = 0
for x in a:
    answer += seen.get(k - x, 0)
    seen[x] = seen.get(x, 0) + 1
print(answer)
```

## Complexity

O(n) time on average, O(d) memory for `d` distinct values.

## Another way

Build the full frequency table first. For each value `v` with `v < k - v` add `count[v] * count[k - v]`, and for
`v == k - v` add `count[v] * (count[v] - 1) // 2`. Same answer, but you must treat the `v == k - v` case separately.
