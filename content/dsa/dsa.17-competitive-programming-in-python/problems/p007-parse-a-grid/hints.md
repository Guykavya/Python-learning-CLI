## Hint 1

The row strings contain no spaces, so `read().split()` gives the two numbers followed by exactly `n` row strings (and removes any `\r`). What does `data[2:2 + n]` hold?

## Hint 2

For each row you need three things: where `S` is, where `E` is, how many `#`. `row.find("S")` returns the 0-based column or `-1`; `row.count("#")` counts walls.

## Hint 3

```text
data = read().split()
n, m = ints
rows = data[2 : 2 + n]
walls = 0
for r in range(n):
    walls += rows[r].count("#")
    c = rows[r].find("S")  -> if c != -1: remember (r+1, c+1)
    similarly E
print the five numbers
```
