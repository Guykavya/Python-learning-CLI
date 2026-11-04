## Hint 1

If you know only the smallest prime factor of `x`, how can you get all of its prime factors, step by step?

## Hint 2

`x = spf[x] * (x // spf[x])`. Repeat with `x // spf[x]` until `x` is 1. Count how many times each prime appears in a
row, because equal primes come out one after another. Then multiply `(exponent + 1)`.

## Hint 3

```
build spf up to max(queries)
for each n:
    ans = 1
    while n > 1:
        p = spf[n]; e = 0
        while n % p == 0: n //= p; e += 1
        ans *= e + 1
    print ans
```
