## Approach

Rule by rule: `lower()`, then `split()` (handles spaces and the empty text), then a character filter with `isalnum()`, then skipping words that became empty, then `"-".join`. Each step was forced by one failing test, which is the point of TDD: the code never contains a feature that no test asked for.

## Code

```python
def slugify(text):
    words = []
    for word in text.lower().split():
        kept = ""
        for ch in word:
            if ch.isalnum():
                kept += ch
        if kept != "":
            words.append(kept)
    return "-".join(words)
```

## Complexity

O(n) for n characters.

## Another way

`"".join(ch for ch in word if ch.isalnum())` replaces the inner loop.
