## Hint 1

`"a = b = c".partition("=")` returns `("a ", "=", " b = c")`. What does it return when there is
no `=`? How can you tell?

## Hint 2

To report "first on line m" you need to remember where each key was first seen. Which data
structure maps a key to a line number?

## Hint 3

```
for n, raw in enumerate(lines, start=1):
    line = raw.strip(); skip empty or '#'
    key, sep, value = line.partition("=")
    if not sep: raise ...
    strip key and value; check unknown; check duplicate; remember first_seen[key] = n
    try: config[key] = schema[key](value)
    except ValueError as e: raise ValueError(f"line {n}: bad value ...") from e
missing = sorted(set(schema) - set(config)); if missing: raise ...
```
