## Approach

This is the standard counting pattern. `get(w, 0)` returns 0 for a word not yet seen, so one
line handles both cases. The dict remembers insertion order, so printing it gives first-seen
order.

## Code

```python
counts = {}
for w in input().lower().split():
    counts[w] = counts.get(w, 0) + 1
if not counts:
    print("No words.")
for word, n in counts.items():
    print(f"{word}: {n}")
```

## Complexity

O(n) for n words: each dict update is O(1) on average.

## Another way

`if w in counts: counts[w] += 1 else: counts[w] = 1`. Or `collections.Counter`, from core.17.
