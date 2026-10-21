## Approach

`sorted` calls the key function on each word and compares the results. A tuple compares item by
item, so `(len(w), w.lower())` compares lengths first and only looks at the lowercase word when
the lengths are equal.

## Code

```python
def sort_by_length(words):
    """Return words sorted by length, then alphabetically ignoring case."""
    return sorted(words, key=lambda w: (len(w), w.lower()))
```

## Complexity

O(n log n) comparisons; each key is computed once per word.

## Another way

Sort twice, relying on stability (core.05): `step = sorted(words, key=str.lower)` then
`sorted(step, key=len)`. The second sort keeps the alphabetical order among equal lengths.
