## Hint 1

If you were adding the numbers on paper, what would you keep track of as you go?

## Hint 2

Keep a running total that starts at 0. Loop over every number from 1 to `n` and add it. Remember that `range(a, b)` stops *before* `b`.

## Hint 3

```
total = 0
for i in range(1, n + 1):
    total = total + i
print total
```
