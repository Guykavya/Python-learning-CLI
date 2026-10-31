## Approach

Describe the whole line, from the first character to the last, and name the two parts:

```
\s*  (?P<key>[A-Za-z_]\w*)  \s*=\s*  (?P<value>.*?)  \s*
```

(the spaces above are only for reading; the real pattern has none)

- `[A-Za-z_]\w*` is an identifier: no spaces, no `=`, so the key ends at the first `=`.
- `(?P<value>.*?)` is **lazy**: it takes as little as possible. Because `fullmatch` forces the
  match to reach the end of the line, the lazy group grows only until the rest (`\s*`) can
  finish the line. So the trailing spaces go to `\s*` and not into the value.
- A greedy `.*` would grab the trailing spaces first, and `\s*` would happily match nothing.

`m.groupdict()` returns `{'key': ..., 'value': ...}`, a fresh dict keyed by group name.

## Code

```python
import re

KV_RE = re.compile(r"\s*(?P<key>[A-Za-z_]\w*)\s*=\s*(?P<value>.*?)\s*")


def parse_kv(line: str) -> dict[str, str] | None:
    m = KV_RE.fullmatch(line)
    if m is None:
        return None
    return m.groupdict()
```

## Complexity

O(n) for most lines. The lazy group retries the tail once per character, which is O(n²) in
theory for a line ending in many spaces, but lines in a settings file are short.

## Another way

Use a greedy value and strip it afterwards:

```python
m = re.fullmatch(r"\s*(?P<key>[A-Za-z_]\w*)\s*=(?P<value>.*)", line)
if m is None:
    return None
return {"key": m["key"], "value": m["value"].strip()}
```

Or without regex: `key, sep, value = line.partition("=")`, then strip both and check the key
with `key.isidentifier()`. (`isidentifier` also accepts non-English letters, which `[A-Za-z_]`
does not.)
