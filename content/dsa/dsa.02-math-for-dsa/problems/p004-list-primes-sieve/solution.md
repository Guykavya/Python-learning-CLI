## Approach

The sieve marks composites instead of testing each number. When `p` is a prime, all its multiples are
composite. Multiples below `p * p` have a smaller prime factor, so they were crossed off earlier. We start at
`p * p`. We only need `p` up to the square root of `n`, because every composite `<= n` has a prime factor
`<= sqrt n`.

## Code

```python
n = int(input())
is_prime = [True] * (n + 1)
is_prime[0] = False
if n >= 1:
    is_prime[1] = False
p = 2
while p * p <= n:
    if is_prime[p]:
        for m in range(p * p, n + 1, p):
            is_prime[m] = False
    p += 1
print(" ".join(str(k) for k in range(2, n + 1) if is_prime[k]))
```

## Complexity

About `n log log n` steps: for `n = 10^6` roughly 2.5 million crossings. Memory O(n). Trial division on every
number costs about `n * sqrt n / log n`, which is a hundred times more for the largest input.

## Another way

Use slice assignment: `is_prime[p*p::p] = [False] * len(range(p*p, n + 1, p))`. It does the crossing in C and
is several times faster. A `bytearray` uses 1 byte per flag instead of 8.
