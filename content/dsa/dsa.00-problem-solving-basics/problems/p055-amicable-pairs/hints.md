## Hint 1

Start with job (1) alone: write a loop that prints the sum of proper divisors of 220 and check you
get 284. Then think about job (2): for each `a`, you can compute `b = sum(a)`. What must be true
about `b`, and what must you then check about `sum(b)`?

## Hint 2

Speed: divisors come in pairs. If `d` divides `a`, so does `a // d`, and one of the two is at most the
square root. So loop `d` only while `d * d <= a`, add both `d` and `a // d`, but add a square root
only once (when `d == a // d`). Start the sum at 1 (1 always divides) and `d` at 2, so `a` itself is
never added. To avoid duplicates and perfect numbers, only accept `b` when `b > a`.

## Hint 3

```
found = False
for a in 2..n:
    s = sum of proper divisors of a   (pairing loop, d*d <= a)
    b = s
    if a < b <= n:
        t = sum of proper divisors of b
        if t == a: print a, b; found = True
if not found: print "none"
```
Write the divisor-sum loop twice (once for `a`, once for `b`); without functions that is fine.
