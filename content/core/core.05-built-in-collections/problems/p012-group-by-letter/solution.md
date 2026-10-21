## Approach

Grouping is a dict whose values are lists. `setdefault` returns the existing list, or stores
and returns a new empty one, so one line handles both cases.

## Code

```python
groups = {}
for word in input().split():
    groups.setdefault(word[0].lower(), []).append(word)
for letter, words in groups.items():
    print(f"{letter}: {' '.join(words)}")
```

## Complexity

O(n) for n words.

## Another way

```python
if letter not in groups:
    groups[letter] = []
groups[letter].append(word)
```
