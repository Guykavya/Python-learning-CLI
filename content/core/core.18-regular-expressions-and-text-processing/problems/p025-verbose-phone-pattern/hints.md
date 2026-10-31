## Hint 1

Write the pattern as a triple-quoted raw string, one piece per line:

```python
PHONE_RE = re.compile(r"""
    (?:\+1[ -]?)?        # optional country code
    ...
""", re.VERBOSE)
```

What does each piece of the one-line pattern above do? Give each its own line and comment.

## Hint 2

The area code is the tricky part. Python does not allow two groups with the same name, so you
cannot write `\((?P<area>...)\)|(?P<area>...)`. Instead capture the brackets too:
`(?P<area>\([2-9]\d{2}\)|[2-9]\d{2})` — this also rejects unbalanced brackets — and strip `()`
from the text in Python.

## Hint 3

```
m = PHONE_RE.fullmatch(s.strip())
if no match: return None
d = m.groupdict()
d["area"] = d["area"].strip("()")
return d
```
