## Approach

`groupby` walks the text once and starts a new group every time the character changes. So each
group is exactly one run. We count the group's items and keep `(char, count)`.

`group` is an iterator, so it has no `len()`. `sum(1 for _ in group)` counts it without building
a list. `len(list(group))` also works.

`decode` repeats each character `count` times and joins the pieces.

## Code

```python
from itertools import groupby


def encode(text):
    return [(char, sum(1 for _ in group)) for char, group in groupby(text)]


def decode(pairs):
    return "".join(char * count for char, count in pairs)
```

## Complexity

Both are O(n), where n is the length of the text.

## Another way

Without `groupby`: loop over the text, keep the current character and a counter, and append a
tuple whenever the character changes (and once more at the end). That is exactly what
`groupby` does for you, and the "once more at the end" is the line people forget.
