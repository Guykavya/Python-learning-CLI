## Approach

Break it into four sub-problems and check each one alone before moving on.

1. **Leap year:** `year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)`.
2. **Days in the month:** 30 for April, June, September, November; 28 or 29 for February; 31 otherwise.
3. **Weekday of the 1st:** Zeller's congruence with `q = 1` gives `h` (0 = Saturday). The number of
   blank cells before the 1st is `(h + 5) % 7` (0 for Monday ... 6 for Sunday).
4. **The grid:** a counter `day` runs from `1 - blanks` to `length`. Values below 1 are blank cells.
   Each cell is `f"{day:>2}"` (or two spaces), with a space before it unless it is the first cell of
   the line. After 7 cells print the line and start a new one. After the loop, print the last line if
   it has any cells. A line is only ever printed right after a real day, so it never ends in spaces.

## Trace

May 2024: `length = 31`. Zeller: `m = 5`, `K = 24`, `J = 20`, `(13 * 6) // 5 = 15`, so
`h = (1 + 15 + 24 + 6 + 5 + 100) % 7 = 151 % 7 = 4`, which is Wednesday.
`blanks = (4 + 5) % 7 = 2`. First week:

| day | cell | col before | line after adding | printed? |
|---|---|---|---|---|
| -1 | `  ` | 0 | `  ` | no |
| 0 | `  ` | 1 | `     ` | no |
| 1 | ` 1` | 2 | `       1` | no |
| 2 | ` 2` | 3 | `       1  2` | no |
| 3 | ` 3` | 4 | `       1  2  3` | no |
| 4 | ` 4` | 5 | `       1  2  3  4` | no |
| 5 | ` 5` | 6 | `       1  2  3  4  5` | yes, col reaches 7 |


## Code

```python
year = int(input())
month = int(input())

# Sub-problem 1: how many days does the month have?
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
if month == 2:
    if leap:
        length = 29
    else:
        length = 28
elif month == 4 or month == 6 or month == 9 or month == 11:
    length = 30
else:
    length = 31

# Sub-problem 2: which weekday is the 1st? (Zeller's congruence)
m = month
y = year
if m < 3:
    m += 12
    y -= 1
k = y % 100
j = y // 100
h = (1 + (13 * (m + 1)) // 5 + k + k // 4 + j // 4 + 5 * j) % 7
# Zeller gives 0 = Saturday, 1 = Sunday, 2 = Monday, ...; shift so that 0 = Monday.
first = (h + 5) % 7

# Sub-problem 3: print the grid, 7 cells per line.
print("Mo Tu We Th Fr Sa Su")
line = ""
col = 0
day = 1 - first          # days before the 1st are blank cells
while day <= length:
    if day < 1:
        cell = "  "
    else:
        cell = f"{day:>2}"
    if col > 0:
        line += " "
    line += cell
    col += 1
    if col == 7:
        print(line)
        line = ""
        col = 0
    day += 1
if col > 0:
    print(line)
```

## Complexity

At most 6 + 31 = 37 cells, so the work is constant: O(1) time and memory (O(d) for `d` days in the month,
if you prefer to count it that way).

## Another way

**Print row by row with nested loops.** Compute the number of rows as `(blanks + length + 6) // 7`,
then for each row `r` and column `c` (0..6) compute `day = r * 7 + c - blanks + 1`, and stop the row
early once `day > length`. This makes the grid structure explicit (rows and columns) and is handy when
you later print several months side by side. The single-counter version above is shorter and has fewer
places for an off-by-one.

## Edge cases

- A month starting on Monday with 28 days (February 2021): exactly 4 rows and no empty line after.
- A month starting on Sunday with 30 or 31 days: 6 blank cells and 6 week lines.
- February in 1900 (28 days) versus 2000 (29 days).
