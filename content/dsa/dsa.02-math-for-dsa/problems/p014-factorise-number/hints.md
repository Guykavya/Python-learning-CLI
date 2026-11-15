## Hint 1

If `i` is the smallest number (above 1) that divides `n`, can `i` be composite? What would that say about a smaller
divisor of `n`?

## Hint 2

So when you divide out `i` completely, all its multiples are gone too and only primes ever divide. Use a `while`
loop to divide as many times as possible, and count. After the main loop, is anything left? What can that leftover be?

## Hint 3

```
parts = []
i = 2
while i * i <= n:
    if n % i == 0:
        e = 0
        while n % i == 0: n //= i; e += 1
        parts.append(f"{i}^{e}")
    i += 1
if n > 1: parts.append(f"{n}^1")
print " ".join(parts), or "1" if parts is empty
```
