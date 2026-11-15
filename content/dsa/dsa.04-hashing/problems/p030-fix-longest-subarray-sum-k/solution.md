## The three bugs

1. **Sign.** The program looks up `total + k`. The needed earlier prefix is `total - k`.
2. **Missing empty prefix.** `seen` starts empty, so blocks that start at index 0 can never match. It must start as
   `{0: -1}` (the empty prefix sits at index -1).
3. **Overwriting the first index.** `seen[total] = i` runs every time, so a repeated prefix sum keeps its **latest** index and
   the blocks come out too short. Store a prefix sum only if it is **not** already in the dictionary.

## Code

```python
n, k = map(int, input().split())
a = [int(x) for x in input().split()]

seen = {0: -1}
total = 0
best = 0
for i, x in enumerate(a):
    total += x
    if total - k in seen:
        best = max(best, i - seen[total - k])
    if total not in seen:
        seen[total] = i
print(best)
```

## Complexity

O(n) time and O(n) memory.

## Another way

For arrays with only non-negative numbers a sliding window works too (dsa.03). With negative numbers a window cannot shrink
safely, which is why the dictionary of prefix sums is needed here.
