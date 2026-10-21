## Hint 1

Fill in the table from the problem for `h = 10, u = 3, d = 1`. Look at the morning heights: 0, 2, 4,
6, 8. What is the pattern? On which morning is the snail close enough that one climb of `u` is enough?
Also: what happens if `u >= h`? What if `u <= d` (and `u < h`)?

## Hint 2

On day `k` the snail starts the morning at `(k - 1) * (u - d)` and reaches `(k - 1) * (u - d) + u`.
It escapes on the first `k` with `(k - 1) * (u - d) + u >= h`, that is
`(k - 1) * (u - d) >= h - u`. So `k - 1` is the **ceiling** of `(h - u) / (u - d)`. Do not use `/`
(floats are inexact for numbers near 10^18). For positive integers, `ceil(a / b)` is `(a + b - 1) // b`.

## Hint 3

```
if u >= h: print 1
elif u <= d: print "never"
else:
    gain = u - d
    need = h - u
    print 1 + (need + gain - 1) // gain
```
Test it against your hand table and against a case where `need` is an exact multiple of `gain`,
for example `h = 9, u = 3, d = 1` (answer 4).
