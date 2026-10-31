# Named groups to a dict: parse key = value

Settings files are full of lines like `port = 8080`. A pattern with **named groups**,
`(?P<key>...)` and `(?P<value>...)`, both checks the line and labels the parts.
`m.groupdict()` then turns the match into a dict in one call.

Write `parse_kv(line: str) -> dict[str, str] | None` in `solution.py`.

- The line is `key = value`. Spaces or tabs around the key, around the `=` and at the ends are allowed.
- The **key** is an identifier: a letter or `_` first, then letters, digits or `_`. No spaces.
- The **value** is everything after the first `=`, with the surrounding whitespace removed.
  It may be empty, may contain spaces in the middle, and may contain more `=` signs.
- Return `{"key": ..., "value": ...}` (exactly these two keys), or `None` if the line does not
  fit (no `=`, empty key, bad key, blank line).

**Example**

```python
parse_kv("port = 8080")             # {'key': 'port', 'value': '8080'}
parse_kv("  title = Hello World  ") # {'key': 'title', 'value': 'Hello World'}
parse_kv("url=http://x.in/?a=1")    # {'key': 'url', 'value': 'http://x.in/?a=1'}
parse_kv("debug =")                 # {'key': 'debug', 'value': ''}
parse_kv("1st = no")                # None   (a key cannot start with a digit)
parse_kv("no equals here")          # None
```
