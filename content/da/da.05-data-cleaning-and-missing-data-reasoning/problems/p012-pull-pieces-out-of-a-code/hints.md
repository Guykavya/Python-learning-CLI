## Hint 1

What does `str.extract` return, and what are the column names when the groups in the pattern have names
(`(?P<name>...)`)? What does it give for a row that does not match? Why can you not use `astype(int)` on a column that
contains missing values, and which type can hold both integers and a missing value?

## Hint 2

```text
pattern = ^(?P<category>[A-Z]{2})-(?P<year>[0-9]{4})-(?P<number>[0-9]{4})$
parts = s.str.strip().str.extract(pattern)          # columns: category, year, number (text or NaN)
parts["year"]   = pd.to_numeric(parts["year"]).astype("Int64")
parts["number"] = pd.to_numeric(parts["number"]).astype("Int64")
return parts
```
