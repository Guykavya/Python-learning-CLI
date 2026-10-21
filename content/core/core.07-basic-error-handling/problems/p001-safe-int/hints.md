## Hint 1

Which single line can fail here, and what is the exact name of the exception it raises for
`"abc"`? Try `int("abc")` in the REPL and read the last line.

## Hint 2

Put only that line inside `try`. In the `except` clause, name that one exception type.

## Hint 3

```
try:
    return int(text)
except ValueError:
    return default
```
