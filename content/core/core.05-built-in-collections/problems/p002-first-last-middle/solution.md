## Approach

Split the line into a list, then use indexing and slicing. Negative index `-1` is always the
last item, whatever the length.

## Code

```python
words = input().split()
print("First:", words[0])
print("Last:", words[-1])
print("Middle:", words[len(words) // 2])
print("Reversed:", " ".join(words[::-1]))
```

## Complexity

Indexing is O(1). Reversing with a slice copies all n references, so it is O(n).

## Another way

`list(reversed(words))` or `words.reverse()` (which changes the list in place and returns `None`).
