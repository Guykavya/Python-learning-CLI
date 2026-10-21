## Hint 1

What does `print` put *between* the values you give it, and what does it put
*after* the last one?

## Hint 2

`sep` replaces the space between values. `end` replaces the newline at the end.
`end=""` means "add nothing at the end".

## Hint 3

```
print(day, month, year, sep="<separator>")
print("Loading...", end="<nothing>")
print("done")
```
