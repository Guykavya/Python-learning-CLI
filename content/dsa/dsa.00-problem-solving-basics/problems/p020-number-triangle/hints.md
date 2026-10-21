## Hint 1

How many rows are there, and on row `i`, what is the last number printed? What does that tell you about the two `range(...)` calls you need?

## Hint 2

Use an outer loop for the row number `i` and an inner loop for the numbers `1` to `i`.
Build the row as a string first (start from `""` and add pieces), then print it once at the end of the row.

## Hint 3

```
read n
for i from 1 to n:
    line = ""
    for j from 1 to i:
        if j > 1: add a space to line
        add str(j) to line
    print line
```
