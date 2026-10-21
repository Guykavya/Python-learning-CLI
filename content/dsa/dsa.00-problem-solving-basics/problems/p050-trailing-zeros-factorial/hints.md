## Hint 1

Every trailing zero is one factor of 10, and 10 = 2 * 5. In `10!`, how many factors 2 are there,
and how many factors 5? Which one runs out first?

## Hint 2

There are always more 2s than 5s, so count the 5s. Multiples of 5 each give one 5. But multiples
of 25 give a **second** 5, multiples of 125 a third, and so on. `n // 5` counts the multiples of 5,
`n // 25` the multiples of 25.

## Hint 3

```
count = 0
power = 5
while power <= n:
    count += n // power
    power *= 5
print count
```
(Or: repeatedly do `n //= 5` and add `n` to the count until `n` is 0.)
