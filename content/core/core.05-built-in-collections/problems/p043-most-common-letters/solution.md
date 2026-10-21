## Approach

Count letters in a dict, then decorate-sort-undecorate with `(-count, letter)` tuples.

## Code

```python
counts = {}
for ch in input().lower():
    if ch.isalpha():
        counts[ch] = counts.get(ch, 0) + 1
top = sorted((-n, ch) for ch, n in counts.items())[:3]
if not top:
    print("No letters")
for neg, ch in top:
    print(f"{ch}: {-neg}")
```

## Complexity

O(n) to count; at most 26 distinct letters to sort for English text.
