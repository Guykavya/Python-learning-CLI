## Hint 1

What does `2024 // 10` give? Do it again, and again. How many steps until the number is 0? How does that relate to the digit count?

## Hint 2

Keep a counter. Each time you drop the last digit with `n //= 10`, add 1 to the counter. Make the number positive first with `abs()`, because `-450 // 10` is `-45` and a negative never reaches 0 the way you expect with `while n > 0`.

## Hint 3

```
n = abs(n)
count = 0
repeat:
    n = n // 10
    count = count + 1
until n is 0
print count
```

A `while n > 0` loop runs zero times for `0`. Either handle `0` separately or make sure the loop body runs at least once.
