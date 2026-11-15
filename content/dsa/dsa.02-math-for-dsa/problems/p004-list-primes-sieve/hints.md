## Hint 1

Instead of asking "is this number prime?" for each number, flip the question: when you meet a prime `p`,
which numbers can you immediately say are *not* prime?

## Hint 2

The multiples of `p`: `2p, 3p, ...`. Multiples smaller than `p * p` were already crossed off by a smaller
prime (`2p` by 2, `3p` by 3, ...), so you can start at `p * p`. And you only need primes `p` with `p * p <= n`.

## Hint 3

```
is_prime = [True] * (n + 1); is_prime[0] = is_prime[1] = False   (careful if n < 1)
p = 2
while p * p <= n:
    if is_prime[p]:
        for m in range(p * p, n + 1, p): is_prime[m] = False
    p += 1
print numbers k with is_prime[k]
```
