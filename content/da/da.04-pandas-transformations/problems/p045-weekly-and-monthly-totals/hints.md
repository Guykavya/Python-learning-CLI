## Hint 1

`resample` is `groupby` for time, but it needs to know which column (or index) holds the dates. How do you give it the
`date` column, and how do you turn the result back into a two-column frame?

## Hint 2

```text
s = daily.set_index("date")["revenue"].resample(freq).sum()
return s.rename_axis("period").reset_index()
```
Check by hand which Monday ends the week of 1 January 2025 (a Wednesday).
