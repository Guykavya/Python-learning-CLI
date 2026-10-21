## Approach

The rules for what `int()` accepts are long (signs, whitespace, underscores between digits,
Unicode digits but not superscripts). Re-implementing them as a check is error-prone, so the
check **is** the conversion: try `int(token)` and treat `ValueError` as "not a number". This is
EAFP at its most useful. The range check is a simple, exact condition, so it is a plain `if`.

## Code

```python
def clean_scores(tokens):
    """Return (scores, rejected): valid 0-100 ints, and the tokens that were not."""
    scores = []
    rejected = []
    for token in tokens:
        try:
            value = int(token)
        except ValueError:
            rejected.append(token)
            continue
        if 0 <= value <= 100:
            scores.append(value)
        else:
            rejected.append(token)
    return scores, rejected
```

## Complexity

O(total length of the tokens).

## Another way

Write a helper `to_int_or_none(token)` (like p001) and use it in the loop. That moves the `try`
into one small function and keeps the loop free of exception handling.
