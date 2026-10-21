## Approach

`*words` is a tuple, maybe empty. Start the best at `""`, which every word ties or beats, so the
empty case returns `""` automatically. Replace only on a strictly greater length so the first
of equal words stays.

## Code

```python
def longest(*words):
    """Return the longest word given (the first one on a tie), or "" if none are given."""
    best = ""
    for w in words:
        if len(w) > len(best):
            best = w
    return best
```

## Complexity

O(n) for n words.

## Another way

`return max(words, key=len, default="")`. `max` returns the first maximal item, and `default`
covers the empty tuple (core.04). Good to know, once you understand the loop it replaces.
