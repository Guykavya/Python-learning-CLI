## Hint 1

Three small jobs, in the `.str` accessor of section 12: remove the outer spaces, squeeze the inner ones, fix the case. Which method squeezes *runs* of whitespace, not just one space? (Hint: the regex `\s+` means "one or more whitespace characters".)

## Hint 2

```text
step 1: s.str.strip()
step 2: ....str.replace(r"\s+", " ", regex=True)
step 3: ....str.title()
chain the three; missing values pass through every .str method untouched
```
