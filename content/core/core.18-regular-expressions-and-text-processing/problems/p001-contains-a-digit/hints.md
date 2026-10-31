## Hint 1

What does `re.search(r"\d", "abc7")` return? And `re.search(r"\d", "abc")`? Try both in the REPL. One of them is a Match object and the other is `None`.

## Hint 2

You need to turn "a Match object or None" into `True` / `False`. Two common ways: `m is not None`, or `bool(m)` (a Match object is always truthy).

## Hint 3

```
has_digit(s):
    m = re.search(r"\d", s)
    return m is not None
```
