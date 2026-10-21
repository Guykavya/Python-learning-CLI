## Hint 1

What changes from one row to the next? Can you write the number of stars in a row using the row number?

## Hint 2

Loop the row number `i` from 1 to `n`. Row `i` has exactly `i` stars. `"*" * 3` gives `"***"`.

## Hint 3

```
for i in range(1, n + 1):
    print("*" * i)
```
