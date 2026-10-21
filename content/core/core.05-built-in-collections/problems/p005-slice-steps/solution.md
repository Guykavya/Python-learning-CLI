## Approach

Every line is one slice. Slices never fail: `words[-3:]` on a two-word list just gives both
words, and `words[1:-1]` on a one-word list is empty.

## Code

```python
words = input().split()
print("Even positions:", " ".join(words[::2]))
print("Odd positions:", " ".join(words[1::2]))
print("Reversed:", " ".join(words[::-1]))
print("Last three:", " ".join(words[-3:]))
print("Without ends:", " ".join(words[1:-1]))
```

## Complexity

Each slice copies the references it selects: O(k) for k selected items.
