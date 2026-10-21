## Approach

Divisors come in pairs `(d, n // d)`, and in every pair the smaller one is at most the square root of `n`.
So try `d` only while `d * d <= n`, and for each divisor add both members of its pair.

Two details:

- The pair `(1, n)` is special: 1 is a proper divisor but `n` is not. So start the sum at 1 (for `n > 1`)
  and begin the loop at `d = 2`. For `n = 1` the sum is 0.
- When `d * d == n` the pair is `(d, d)`, the same number twice. Add it only once.

## Trace

Input `36` (sum starts at 1):

| d | d * d <= 36? | 36 % d | partner | total after |
|---|---|---|---|---|
| 2 | yes | 0 | 18 | 1 + 2 + 18 = 21 |
| 3 | yes | 0 | 12 | 21 + 3 + 12 = 36 |
| 4 | yes | 0 | 9 | 36 + 4 + 9 = 49 |
| 5 | yes | 1 | | 49 |
| 6 | yes | 0 | 6 (same as d) | 49 + 6 = 55 |
| 7 | no (49) | | | loop ends |

`55 > 36`, so `abundant`.

## Code

```python
n = int(input())

if n == 1:
    total = 0
else:
    total = 1  # 1 divides every n > 1; its partner n is not a proper divisor

d = 2
while d * d <= n:
    if n % d == 0:
        total += d
        partner = n // d
        if partner != d:
            total += partner
    d += 1

if total == n:
    print("perfect")
elif total > n:
    print("abundant")
else:
    print("deficient")
```

## Complexity

About sqrt(n) loop rounds: O(sqrt(n)) time, O(1) space. For `n` near 10 to the power 12 that is about a
million rounds instead of a trillion.

## Another way

**Use the prime factorisation.** If `n = p^a x q^b x ...`, the sum of **all** divisors is
`(1 + p + ... + p^a) x (1 + q + ... + q^b) x ...`; subtract `n` to get the proper-divisor sum. Finding the
prime factors also takes up to sqrt(n) steps in the worst case, but it stops early when `n` breaks into small
primes, and the formula is how mathematicians reason about perfect numbers. The pair method is simpler to
get right, so prefer it unless you already have the factorisation.

## Edge cases

- `n = 1`: no proper divisors, sum 0, deficient.
- Primes: the only proper divisor is 1, so they are always deficient.
- Perfect squares (36, 49, ...): the square root is a divisor that pairs with itself; count it once.
