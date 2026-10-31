## Hint 1

Which quantifier means "between 4 and 6 times"? Try `re.fullmatch(r"[0-9]{4,6}", "12345")` and the same with `"1234567"`.

## Hint 2

Why `fullmatch` and not `match`? Run `re.match(r"[0-9]{4,6}", "1234567")`: it succeeds, because the first six digits fit and `match` does not care about the rest. And why `[0-9]` and not `\d`? Try `re.fullmatch(r"\d{4}", "१२३४")`.

## Hint 3

```
valid_pin(s):
    return re.fullmatch(r"[0-9]{4,6}", s) is not None
```
