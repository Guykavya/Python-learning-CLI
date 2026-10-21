## Hint 1

Which number changes from line to line? Which numbers stay the same? What should your loop variable be?

## Hint 2

Loop `i` over `range(1, k + 1)`. On each step, compute `n * i` and print one line. An f-string lets you put the three numbers in place with the exact spacing.

## Hint 3

```
for i in range(1, k + 1):
    print(f"{n} x {i} = {n * i}")
```
