## Approach

Make **one** iterator `it` from the input. Give it to `takewhile`, which yields the header
lines while they are not blank. To find out that a line is blank, `takewhile` must read it, and
that line is then gone from `it`. Usually this "swallowed item" is a trap. Here it is exactly
what we want: the separator disappears.

After the header loop, `it` sits at the first body line, so `list(it)` is the body. One pass,
works on lists and generators.

## Code

```python
from itertools import takewhile


def split_message(lines):
    it = iter(lines)
    headers = {}
    for line in takewhile(lambda line: line.strip() != "", it):
        key, value = line.split(":", 1)
        headers[key.strip()] = value.strip()
    body = list(it)
    return headers, body
```

## Complexity

O(number of lines) time. The body list is O(body size) memory.

## Another way

A plain loop over `it` with `break` at the first blank line, then `list(it)`. It does the same
as `takewhile`.

`dropwhile(test, lines)` gives you everything **from** the first blank line on, separator
included. It does not help with the headers, and you cannot use it on the same generator after
reading the headers from it.
