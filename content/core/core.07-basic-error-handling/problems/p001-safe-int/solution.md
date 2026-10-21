## Approach

`int(text)` is the only operation, and it fails in exactly one expected way for text that is not a
whole number: `ValueError`. Catch that type and return the default. Any other exception, such as
`TypeError` for `None`, means the caller has a bug, so it is left to propagate.

## Code

```python
def to_int(text, default=0):
    """Return int(text), or default if text is not a whole number."""
    try:
        return int(text)
    except ValueError:
        return default
```

## Complexity

O(n) in the length of the text, which is what `int` itself costs.

## Another way

An LBYL version checks first: `if text.strip().lstrip("+-").isdigit(): return int(text)`. It is
longer and still wrong for inputs such as `"²"` (isdigit is True, int fails) and `"1_000"` (int
accepts it). Letting `int` be the check (EAFP) is both shorter and exactly right.
