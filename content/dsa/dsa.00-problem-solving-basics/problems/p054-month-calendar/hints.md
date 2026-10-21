## Hint 1

Which facts do you need before you can print anything? Write them as questions: how many days,
and how many blank cells come first? Solve each separately and print it to check, for example
May 2024 should give 31 days and 2 blanks.

## Hint 2

Zeller's `h` is 0 for Saturday, 1 for Sunday, 2 for Monday. You want 0 for Monday, ..., 5 for
Saturday, 6 for Sunday. Try `(h + 5) % 7` on all three examples. For the grid, a neat trick is to
let a counter `day` start at `1 - blanks`: values below 1 are blank cells, 1..length are real days.
Keep a column counter `col`; put a space before every cell except the first in a line.

## Hint 3

```
print header
line = ""; col = 0; day = 1 - blanks
while day <= length:
    cell = "  " if day < 1 else f"{day:>2}"
    if col > 0: line += " "
    line += cell
    col += 1
    if col == 7: print line; line = ""; col = 0
    day += 1
if col > 0: print line      # the last, incomplete week
```
Because a line is printed right after a real day, it can never end with a space.
