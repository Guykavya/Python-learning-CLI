## Approach

When you are at position `j` with value `x`, you need an earlier value `target - x`. Keep a dictionary from value to
index of everything to the left. One lookup answers the question. Check first, store second, so that an element never
pairs with itself.

## Code

```python
n, target = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {}
for j, x in enumerate(a):
    need = target - x
    if need in seen:
        print(seen[need], j)
        break
    seen[x] = j
```

## Complexity

O(n) time on average, O(n) memory.

## Another way

Sort pairs of `(value, index)` and use two pointers (dsa.03): O(n log n), and you must carry the original indices.
The brute force with two nested loops is O(n^2).
