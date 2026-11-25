## Hint 1

Which regex class means "not a digit", and what do you replace those characters with? A phone that starts with `91`
might be a country code or the start of a real number. What do you know that tells the two apart (hint: how many
characters come after the `91`)? Which `str` method checks that the **whole** text has a given shape?

## Hint 2

```text
digits = s.str.replace(r"\D", "", regex=True)
digits = digits.str.replace(r"^(?:91|0)(?=\d{10}$)", "", regex=True)   # prefix only if exactly 10 digits follow
valid  = digits.str.fullmatch(r"[6-9]\d{9}", na=False)
return digits.where(valid)         # NaN where not valid
```
`(?=...)` is a lookahead: it looks at what follows without using it up.
