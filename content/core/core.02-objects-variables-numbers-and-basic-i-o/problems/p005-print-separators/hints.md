## Hint 1

`print(a, b, c)` puts a single space between items. Which parameter controls that space?

## Hint 2

`sep` is placed **between** items. `end` is placed **after** the last item, and its default is `"\n"`.
If you change `end`, you replace the newline too.

## Hint 3

```
print(a, b, c, sep="-")
print(a, b, c, sep="")
print(a, b, c, sep=", ", end="!" + newline)
print(a, end=" and ")
print(c)
```
