## Approach

The lcm of a set of numbers has, for each prime, the largest exponent seen in any of them. Among `1..n`, the largest
power of a prime `p` that appears is `p^k` with `p^k <= n < p^(k+1)`. So `lcm(1..n)` is the product of these
`p^k` over all primes `p <= n`. A sieve lists the primes.

## Code

```python
MOD = 10**9 + 7
n = int(input())

is_prime = bytearray([1]) * (n + 1)
is_prime[0] = 0
if n >= 1:
    is_prime[1] = 0
p = 2
while p * p <= n:
    if is_prime[p]:
        is_prime[p * p::p] = bytearray(len(range(p * p, n + 1, p)))
    p += 1

ans = 1
for p in range(2, n + 1):
    if is_prime[p]:
        pk = p
        while pk * p <= n:
            pk *= p
        ans = ans * pk % MOD
print(ans)
```

## Complexity

Sieve `O(n log log n)`, then about `n / ln n` primes with a tiny power loop each (most primes above `sqrt(n)` have `k = 1`).
Total well under a second for `n = 10^6`. The fold with big integers costs about `n` steps of `O(n)` size each: minutes.

## Another way

For primes `p > sqrt(n)` the power is just `p`, so you can handle them in one product. Or keep the fold
`ans = lcm(ans, i)` modulo something? That does **not** work: you cannot take gcd of numbers that were reduced mod `10^9 + 7`.
The prime-power view is what makes the modulus possible.
