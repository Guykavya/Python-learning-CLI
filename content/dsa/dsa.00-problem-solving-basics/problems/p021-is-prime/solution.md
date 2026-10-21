## Approach

Numbers below 2 are not prime, so `is_prime` starts as `n >= 2`.

If `n` has a divisor `a` with `n = a x b`, then `a` and `b` cannot both be bigger than the square root of `n`,
because then `a x b` would be bigger than `n`. So if `n` has any divisor other than 1 and itself, it has one
that is at most the square root of `n`. We try `d = 2, 3, 4, ...` only while `d * d <= n`. Writing
`d * d <= n` keeps everything in exact integers (no `sqrt`, no floats). The moment a divisor is found
the loop stops.

For `n` up to 10 to the power 12, the square root is 10 to the power 6, so at most about a million tries
instead of a trillion.

## Trace

Input `91`:

| d | d * d | d * d <= 91? | 91 % d | is_prime after |
|---|---|---|---|---|
| 2 | 4 | yes | 1 | True |
| 3 | 9 | yes | 1 | True |
| 4 | 16 | yes | 3 | True |
| 5 | 25 | yes | 1 | True |
| 6 | 36 | yes | 1 | True |
| 7 | 49 | yes | 0 | False -> loop ends |

Printed: `not prime`.

## Code

```python
n = int(input())

is_prime = n >= 2
d = 2
while is_prime and d * d <= n:
    if n % d == 0:
        is_prime = False
    d += 1

if is_prime:
    print("prime")
else:
    print("not prime")
```

## Complexity

At most about the square root of `n` loop rounds: O(sqrt(n)) time, O(1) space.
For a 12-digit prime that is about one million rounds, well under a second.
A loop up to `n` would need about a trillion rounds, which takes hours.

## Another way

**Skip even divisors.** After checking `d = 2` separately, try only odd `d = 3, 5, 7, ...` (step 2).
That halves the work. You can go further and try only numbers of the form 6k - 1 and 6k + 1, which
cuts it to a third. These matter when you must test many numbers. When you need to know which of
**all** numbers up to some limit are prime, a sieve (crossing out multiples, covered later with lists)
is much faster than testing each number on its own.

## Edge cases

- `n <= 1` (including 0 and negatives): not prime, the loop never runs.
- `n = 2` and `n = 3`: `2 * 2 > 3`, so the loop never runs and they are prime.
- Squares of primes such as `49` or `999983 * 999983`: the only small divisor is exactly the square root, so `d * d <= n` must use `<=`.
