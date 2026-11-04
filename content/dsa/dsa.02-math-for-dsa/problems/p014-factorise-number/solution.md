## Approach

Take `i = 2, 3, 4, ...`. The first `i` that divides `n` is prime (a composite divisor would have a smaller prime factor
which would have been found first). Divide `n` by `i` until it no longer divides, counting the exponent. This
also removes all composite multiples of `i`, so we never see them as divisors. The loop stops when `i * i > n`: whatever
remains (if greater than 1) has no divisor up to its square root, so it is itself a prime.

## Code

```python
q = int(input())
for _ in range(q):
    n = int(input())
    parts = []
    i = 2
    while i * i <= n:
        if n % i == 0:
            e = 0
            while n % i == 0:
                n //= i
                e += 1
            parts.append(f"{i}^{e}")
        i += 1
    if n > 1:
        parts.append(f"{n}^1")
    print(" ".join(parts) if parts else "1")
```

## Complexity

O(sqrt n) per number in the worst case (when `n` is prime or twice a prime): about 10^6 steps for `n = 10^12`.
When `n` has small factors the loop ends sooner because `n` shrinks, and `i * i <= n` is checked against the shrunk value.

## Another way

Sieve the primes up to 10^6 first and divide only by those (about 78000 candidates instead of a million).
For many queries with small `n`, the smallest-prime-factor sieve in the next problem is much faster.
