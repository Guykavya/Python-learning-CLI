## Approach

One pass over the lines with `enumerate(..., start=1)`, so every message knows its line number.
Each structural problem is a plain `if` with its own message. The value conversion is the only
step whose rules belong to someone else (the converter), so it is the only `try`, and it catches
only `ValueError`: that is the converter's way of saying "bad value". Re-raising `from e` keeps
the converter's explanation as the cause, so the traceback shows both "expected yes or no" and
"line 4: bad value for 'fullscreen'". A dict `first_seen` remembers where each key appeared.
Missing settings can only be known at the end, with a set difference.

## Code

```python
def parse_config(lines, schema):
    """Parse 'key = value' lines using schema converters; raise ValueError 'line N: ...' on problems."""
    config = {}
    first_seen = {}
    for n, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            raise ValueError(f"line {n}: expected 'key = value', got {line!r}")
        key, value = key.strip(), value.strip()
        if key not in schema:
            raise ValueError(f"line {n}: unknown setting {key!r}; known settings: {', '.join(sorted(schema))}")
        if key in first_seen:
            raise ValueError(f"line {n}: {key!r} is set twice (first on line {first_seen[key]})")
        first_seen[key] = n
        try:
            config[key] = schema[key](value)
        except ValueError as e:
            raise ValueError(f"line {n}: bad value for {key!r}: {value!r}") from e
    missing = sorted(set(schema) - set(config))
    if missing:
        raise ValueError(f"missing settings: {', '.join(missing)}")
    return config
```

## Complexity

O(L + s log s) for L total characters and s schema keys.

## Another way

Collect **all** problems in a list instead of raising at the first, then raise one `ValueError`
whose message joins them with newlines. Users fixing a long file prefer seeing every problem at
once; the trade-off is a little more code and a decision about what to do after a bad line.
