## Hint 1

If `n` is composite, it is `a * b` with `1 < a <= b`. How big can the smaller factor `a` be, compared with
`n`? (Think: what if both `a` and `b` were bigger than the square root of `n`?)

## Hint 2

So you only need to test divisors `i` with `i * i <= n`. Which small numbers (0, 1, 2) need special treatment
before the loop?

## Hint 3

```
if n < 2: composite
i = 2
while i * i <= n:
    if n % i == 0: composite
    i += 1
prime
```
