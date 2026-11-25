## Hint 1

Which two `str` methods remove spaces and make everything lower case? Why does the order "clean, then check" matter for
`ASHA@MAIL.EXAMPLE`: what would the pattern say about it before and after lower-casing? Which method requires the
*whole* text to match, and how do you keep only the values that passed (`where`)?

## Hint 2

```text
e = s.str.strip().str.lower()
ok = e.str.fullmatch(r"[a-z0-9._+-]+@[a-z0-9-]+(\.[a-z0-9-]+)+", na=False)
return e.where(ok)        # keeps the cleaned text where ok is True, NaN elsewhere
```
