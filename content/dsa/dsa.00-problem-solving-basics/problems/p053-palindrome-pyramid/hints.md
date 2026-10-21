## Hint 1

Look at one row, say row 4 of a pyramid with `n = 5`: ` 1234321`. Split it into three parts:
the spaces, the part going up, the part coming down. How long is each part, in terms of `i` and `n`?

## Hint 2

Build each row as a string, starting with `" " * (n - i)`. Add the rising part with
`for v in range(1, i + 1)` and the falling part with `for v in range(i - 1, 0, -1)`. Add the digit
`v % 10` each time (for example with `f"{v % 10}"`). Print the row once it is complete.

## Hint 3

```
for i in 1..n:
    line = " " * (n - i)
    for v in 1..i:          line += digit of (v % 10)
    for v in i-1 down to 1: line += digit of (v % 10)
    print line
```
Check that the peak (the middle digit) is written only once.
