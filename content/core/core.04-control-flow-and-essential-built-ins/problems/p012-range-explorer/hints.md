## Hint 1

Let Python's own `range` do the work. Your job is printing it and checking the special cases.

## Hint 2

`len(range(...))` gives the count without a loop. An empty range is falsy.

## Hint 3

Build the first line as a string: start with `""` and add `str(n) + " "` for each number,
then `.strip()` it. Or print each number with `end=" "` and then `print()`.
