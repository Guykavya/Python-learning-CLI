## Approach

Two layers, planned separately.

1. **Is `x` prime?** If `x = a * b` with `a <= b`, then `a * a <= a * b = x`. So any composite `x`
   has a divisor `d` with `d * d <= x`. Test only those. For `x` near 224737 that is about 470
   numbers instead of 224000. Since we only test odd `x`, even divisors can never divide it, so
   start at `d = 3` and step by 2.
2. **Find the k-th.** Count 2 by hand (it is the only even prime). Then walk through odd numbers
   3, 5, 7, ..., test each, and count the primes. Stop as soon as the count reaches `k`; the current
   `x` is the answer.

## Trace

Input `k = 4` (expected 7):

| x | d values tried | is_prime | count |
|---|---|---|---|
| (2) | | | 1 |
| 3 | none (3 * 3 > 3) | True | 2 |
| 5 | none (3 * 3 > 5) | True | 3 |
| 7 | none (3 * 3 > 7) | True | 4, loop stops |

Output: `7`. (For `x = 9`, `d = 3` gives `3 * 3 <= 9` and `9 % 3 == 0`, so 9 is rejected.)

## Code

```python
k = int(input())

if k == 1:
    print(2)
else:
    count = 1        # 2 is already counted
    x = 1
    while count < k:
        x += 2       # only odd numbers can be primes now
        is_prime = True
        d = 3
        while d * d <= x:
            if x % d == 0:
                is_prime = False
                break
            d += 2
        if is_prime:
            count += 1
    print(x)
```

## Complexity

If the answer is `P` (about 224737 for `k = 20000`), we test about `P / 2` candidates, each with at
most `sqrt(P) / 2` divisions: O(P * sqrt(P)) in the worst case, but most composites are rejected after
one or two divisions, so in practice it runs in well under a second. Memory is O(1).

## Another way

**Sieve of Eratosthenes.** Make a table of "is prime" flags up to a limit (say 230000), and for each
prime cross out its multiples. It is much faster (O(P log log P)) but needs a list of flags, which you
will meet later in the course. Prefer the sieve when you need *many* primes or many queries; prefer
trial division when you have one number to test or no memory to spare.

## Edge cases

- `k = 1`: answer 2, handled separately because the loop only looks at odd numbers.
- Squares of primes (9, 25, 49, ...): rejected only if the condition is `d * d <= x`.
