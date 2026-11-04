## Hint 1

Take `lcm(1..10) = 2520 = 2^3 * 3^2 * 5 * 7`. Where do the exponents 3 and 2 come from? Which numbers up to 10
contain `2^3` and `3^2`?

## Hint 2

For each prime `p <= n`, find the largest `p^k <= n` with a loop: start with `pk = p`, and while `pk * p <= n`,
multiply `pk` by `p`. Use a sieve to list the primes.

## Hint 3

```
sieve primes up to n
ans = 1
for each prime p <= n:
    pk = p
    while pk * p <= n: pk *= p
    ans = ans * pk % MOD
print ans
```
