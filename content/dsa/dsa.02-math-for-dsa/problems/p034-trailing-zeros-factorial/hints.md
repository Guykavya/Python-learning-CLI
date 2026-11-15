## Hint 1

Take `p = 5`, `n = 100`. Which numbers from 1 to 100 are divisible by 5? How many? Each gives at least one factor 5. Which of
them give a **second** factor 5?

## Hint 2

The multiples of 25 give a second factor, those of 125 a third. So the total is
`n // 5 + n // 25 + n // 125 + ...`. Notice that `n // 25 = (n // 5) // 5`. You can divide again and again by `p`.

## Hint 3

```
total = 0
while n > 0:
    n = n // p
    total = total + n
print(total)
```
Trace it for `n = 100, p = 5`: n becomes 20, 4, 0.
