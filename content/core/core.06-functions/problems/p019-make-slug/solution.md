## Approach

Normalise first: lowercase, and turn every character that is not a letter or digit into a space.
`split()` with no argument then does the hard part: it treats any run of spaces as one gap and
ignores spaces at the ends. Joining with `sep` builds the slug. Truncation can leave a partial
separator at the end, so strip whole `sep` suffixes in a loop. The `/` and `*` in the signature
make the options impossible to pass by position.

## Code

```python
def make_slug(text, /, *, sep="-", max_length=None):
    """Return a lowercase URL slug of text."""
    cleaned = "".join(ch if ch.isalnum() else " " for ch in text.lower())
    slug = sep.join(cleaned.split())
    if max_length is not None:
        slug = slug[:max_length]
        while sep and slug.endswith(sep):
            slug = slug[:-len(sep)]
    return slug
```

## Complexity

O(n) for a text of n characters.

## Another way

A single loop with a flag `in_gap`: append characters to a list, and when a letter follows a gap
(and the list is not empty) append `sep` first. This avoids the intermediate string but is
longer and easier to get wrong at the edges.
