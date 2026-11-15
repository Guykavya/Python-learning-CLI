## Approach

Euclid's rule `gcd(a, b) = gcd(b, a % b)` keeps the common divisors the same while making the numbers
smaller. We repeat until the second number is 0; then `gcd(a, 0) = a`.

## Code

```python
q = int(input())
for _ in range(q):
    a, b = (int(x) for x in input().split())
    while b != 0:
        a, b = b, a % b
    print(a)
```

## Complexity

O(log min(a, b)) steps per pair. After two steps the number at least halves, so for 10^18 there are at most
about 120 steps (and the worst case is two neighbouring Fibonacci numbers). The zero cases need no special code:
`gcd(0, 5)` becomes `(5, 0)` after one step; `gcd(5, 0)` is already done; `gcd(0, 0)` returns 0.

## Another way

Recursion: `def g(a, b): return a if b == 0 else g(b, a % b)`. Depth is at most about 90, well within
Python's limit. A subtraction version (`while a != b: subtract the smaller from the larger`) is correct but
needs up to 10^18 steps for `gcd(10^18, 1)`.
