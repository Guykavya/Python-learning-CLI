## Hint 1

You want the **whole** string (after stripping) to have the shape, not just some part of it.
Which function checks the whole string: `re.search`, `re.match` or `re.fullmatch`? What does
`re.search(r"(\d+)\.(\d+)\.(\d+)", "1.2.3.4")` find?

## Hint 2

Put brackets around each number: `(\d+)`. The dots between them must be escaped, `\.`,
or a bare `.` would accept *any* character (`1x2x3`). The optional `v` is `[vV]?`, and it is
**outside** the groups so it is not captured.

## Hint 3

```
m = re.fullmatch(r"[vV]?(\d+)\.(\d+)\.(\d+)", s.strip())
if m is None: return None
return tuple of int(g) for g in m.groups()
```
