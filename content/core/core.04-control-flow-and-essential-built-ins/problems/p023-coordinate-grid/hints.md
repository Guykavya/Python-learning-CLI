## Hint 1

One loop for the rows; inside it, one loop for the columns. Where does the line end?

## Hint 2

Build each row as a string, then print it after the inner loop finishes.

## Hint 3

```
for r in range(1, R + 1):
    line = ""
    for c in range(1, C + 1):
        line += f"({r},{c}) "
    print(line.strip())
```
