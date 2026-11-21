## Hint 1

Work line by line with `enumerate(text.splitlines(), start=1)` so you always know the line number. Which string method splits at the first `=` only and tells you whether there was one?

## Hint 2

```text
for number, raw in enumerate(lines, 1):
    line = raw.strip(); skip if empty or starts with "#"
    drop a leading "export "
    name, sep, value = line.partition("=")
    no sep -> error "line N: expected NAME=value"
    name must fullmatch [A-Za-z_][A-Za-z0-9_]* -> else error
    value = value.strip()
    if value starts with a quote: it must be at least 2 chars and end with the same quote; strip both
    values[name] = value
```
