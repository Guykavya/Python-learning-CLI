## Approach

Every composite `m <= r` has a prime factor `p <= sqrt(r)`. So if we cross off, inside `l..r`, the multiples of all primes
up to `sqrt(r)` (at most 10^5), only primes remain. The table covers just `r - l + 1 <= 10^6` numbers, and the base primes
come from an ordinary sieve of size `10^5`.

## Code

```python
l, r = [int(x) for x in input().split()]

limit = 1
while limit * limit <= r:
    limit += 1
small = [True] * (limit + 1)
base = []
for i in range(2, limit + 1):
    if small[i]:
        base.append(i)
        for m in range(i * i, limit + 1, i):
            small[m] = False

size = r - l + 1
seg = bytearray([1]) * size
for p in base:
    if p * p > r:
        break
    start = max(p * p, (l + p - 1) // p * p)
    for m in range(start, r + 1, p):
        seg[m - l] = 0
if l <= 1:
    for v in range(l, min(r, 1) + 1):
        seg[v - l] = 0

count = 0
total = 0
for j in range(size):
    if seg[j]:
        count += 1
        total += l + j
print(count)
print(total)
```

## Complexity

Sieve of the base: O(sqrt(r) log log r). Segment: about `(r - l) log log r` crossings, plus O(r - l) to count. For 10^6
numbers near 10^10 it takes about 1 second in plain Python; a slice assignment `seg[start - l::p] = bytes(...)` is faster.
Trial division of every number in the range costs about 10^6 * 10^5 / ln: hopeless.

## Another way

Use slice assignment for the inner loop: `seg[start - l::p] = bytes(len(range(start - l, size, p)))`. Or a deterministic
Miller-Rabin test on each number (works, but much more code and needs fast modular exponentiation: you have it from this
module, but a sieve is simpler here).
