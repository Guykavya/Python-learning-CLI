## Approach

`print()` turns each argument into text, writes `sep` between them, and writes `end` after the last one.
The defaults are `sep=" "` and `end="\n"`. Changing them changes the layout without any string building.

## Code

```python
a = input()
b = input()
c = input()
print(a, b, c, sep="-")
print(a, b, c, sep="")
print(a, b, c, sep=", ", end="!\n")
print(a, end=" and ")
print(c)
```

## Why it works

- Line 3 replaces the default `end`, so it must put the newline back itself: `"!\n"`.
- Line 4 is two calls. The first one ends with `" and "` instead of a newline, so the second
  call continues on the same line.

## Another way

`print(a + "-" + b + "-" + c)` gives the same text for line 1, but it only works with strings
and is harder to read. `sep` also works with numbers: `print(1, 2, 3, sep="-")` prints `1-2-3`.
