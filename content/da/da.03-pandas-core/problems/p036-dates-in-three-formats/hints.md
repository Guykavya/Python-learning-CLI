## Hint 1

Chapter 13.2 does it for three formats by hand: parse the whole column with one format and `errors="coerce"` (failures become `NaT`), then use `fillna` to fill the remaining gaps from the next format. How do you turn "three formats written by hand" into "any number of formats"?

## Hint 2

```text
text   = s as string, stripped
parsed = a Series of NaT with the same index as s (dtype datetime64)
for f in formats:
    attempt = pd.to_datetime(text, format=f, errors="coerce")
    parsed  = parsed.fillna(attempt)          # earlier formats win: fillna only touches the gaps
unparsed = original values of s where parsed is NaT and s is not missing, as a list
```
`fillna` is what makes the **order** of the formats decide ambiguous texts.
