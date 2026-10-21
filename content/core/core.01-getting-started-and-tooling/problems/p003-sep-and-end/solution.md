## Approach

`print(a, b, c)` converts each value to text, joins them with `sep` (default
`" "`) and finishes with `end` (default `"\n"`). Change those two defaults.

## Code

```python
day = 18
month = 10
year = 2026

print(day, month, year, sep="/")
print("Loading...", end="")
print("done")
```

## Why

`sep="/"` puts a slash between the three numbers. Notice that `print` converts the
integers to text for you; you never need `str()` here. `end=""` stops the
newline after `Loading...`, so `done` lands right after it.

## Another way

`print(str(day) + "/" + str(month) + "/" + str(year))` gives the same text but is
longer and needs `str()` because `+` cannot join numbers and strings.
