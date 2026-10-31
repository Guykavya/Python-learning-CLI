## Approach

### to_snake: find the boundaries, then lower-case

There are two kinds of boundary, so use two passes:

1. `([A-Z]+)([A-Z][a-z])` → `\1_\2`: the **end of an acronym**. On `HTTPServer` the greedy
   `[A-Z]+` first grabs `HTTPS`, then the next part needs a capital and a small letter, so it
   gives back the `S`. Group 1 is `HTTP`, group 2 is `Se`: `HTTP_Server`.
2. `([a-z0-9])([A-Z])` → `\1_\2`: a small letter or digit followed by a capital.
   `getHTTP_Response` → `get_HTTP_Response`.

Then `.lower()`. The order matters only for readability here; both passes look for different
pairs.

### to_camel: replace `_x` by `X`

The replacement depends on the matched text, so use a **function**: `m.group(1).upper()`.
The lookbehind `(?<=[a-z0-9])` demands a letter or digit before the `_`, so leading underscores
(`_private`, `__init__`) are not touched, and it does not consume that character.

## Code

```python
import re

ACRONYM_END_RE = re.compile(r"([A-Z]+)([A-Z][a-z])")
LOWER_UPPER_RE = re.compile(r"([a-z0-9])([A-Z])")
UNDERSCORE_RE = re.compile(r"(?<=[a-z0-9])_([a-z0-9])")


def to_snake(name: str) -> str:
    s = ACRONYM_END_RE.sub(r"\1_\2", name)
    s = LOWER_UPPER_RE.sub(r"\1_\2", s)
    return s.lower()


def to_camel(name: str) -> str:
    return UNDERSCORE_RE.sub(lambda m: m.group(1).upper(), name)
```

## Complexity

O(n) per pass, so O(n) overall.

## Another way

`to_snake` with lookarounds, inserting `_` at **positions** (zero-width matches):

```python
re.sub(r"(?<=[a-z0-9])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])", "_", name).lower()
```

`to_camel` without regex: `parts = name.split("_")` and join `parts[0]` with each later part
capitalised. That breaks leading underscores (`"_private".split("_")` starts with `""`), which
is exactly what the lookbehind version handles for free.

Note that the round trip is lossy for acronyms: `to_camel(to_snake("HTTPServer"))` is
`httpServer`. Information about which letters were capitals is gone after `.lower()`.
