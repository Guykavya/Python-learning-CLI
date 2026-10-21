## Approach

**Job 1: sum of proper divisors, fast.** Divisors come in pairs `(d, a // d)`, and the smaller one of
each pair is at most `sqrt(a)`. So loop `d` from 2 while `d * d <= a`; whenever `d` divides `a`, add
`d` and `a // d`, except when they are equal (a perfect square), where you add it once. Start the sum
at 1, because 1 is a proper divisor of every `a >= 2`, and we never add `a` itself.

**Job 2: find the pairs.** For each `a` from 2 to `n`, compute `b = s(a)`. A pair is only possible if
`a < b <= n`:

- `b > a` makes each pair appear once, from its smaller member, and rules out perfect numbers (`b == a`).
- `b <= n` is the limit from the statement.

Then compute `s(b)` with the same loop; if it equals `a`, print the pair. Looping `a` upward prints
pairs in increasing order of `a` automatically. A flag `found` remembers whether to print `none`.

## Trace

Divisor-sum loop for `a = 220` (sqrt is about 14.8):

| d | 220 % d == 0? | added | s |
|---|---|---|---|
| (start) | | 1 | 1 |
| 2 | yes | 2 + 110 | 113 |
| 3 | no | | 113 |
| 4 | yes | 4 + 55 | 172 |
| 5 | yes | 5 + 44 | 221 |
| 6..9 | no | | 221 |
| 10 | yes | 10 + 22 | 253 |
| 11 | yes | 11 + 20 | 284 |
| 12..14 | no | | 284 |

`b = 284 > 220`. The same loop on 284 gives 1 + (2 + 142) + (4 + 71) = 220 = `a`, so `220 284` is printed.

## Code

```python
n = int(input())

found = False
for a in range(2, n + 1):
    # Sum of proper divisors of a: pair each divisor d <= sqrt(a) with a // d.
    s = 1
    d = 2
    while d * d <= a:
        if a % d == 0:
            s += d
            if d != a // d:
                s += a // d
        d += 1
    b = s
    if b > a and b <= n:
        # Now the sum of proper divisors of b must come back to a.
        t = 1
        d = 2
        while d * d <= b:
            if b % d == 0:
                t += d
                if d != b // d:
                    t += b // d
            d += 1
        if t == a:
            print(a, b)
            found = True
if not found:
    print("none")
```

## Complexity

Each divisor sum costs about `sqrt(a)` steps, so the whole search is about `n * sqrt(n)` steps:
O(n sqrt n), roughly 3.5 million for `n = 30000`. The naive "try every d below a" version is O(n^2),
about 450 million, which is far too slow. Memory is O(1).

## Another way

**Divisor-sum sieve.** Make a table `s` of size `n + 1` filled with 0, and for every `d` from 1 to
`n // 2` add `d` to `s[2d], s[3d], ...`. That fills in every divisor sum at once in O(n log n), after
which checking pairs is instant. It needs a list, which comes later in the course, and it only helps
when you need the sums of *all* numbers up to `n`. To test a single number, the square-root loop is better.

## Edge cases

- `n < 284`: no pair, print `none`.
- `n = 284`: the first pair is included (`b <= n`).
- Perfect numbers 6, 28, 496, 8128: `b == a`, rejected by `b > a`.
- Perfect squares: the square root must be added once.
