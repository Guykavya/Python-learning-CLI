## Hint 1

Write one character class that matches a single hex digit. You need three ranges inside the same brackets. Test it with `re.fullmatch(r"[...]", "B")`.

## Hint 2

One hex digit is not enough: the whole string must be hex digits. Which quantifier means "one or more"? And which function makes sure the match covers the **whole** string, from the first character to the last?

## Hint 3

```
only_hex(s):
    return re.fullmatch(r"[0-9a-fA-F]+", s) is not None
```
