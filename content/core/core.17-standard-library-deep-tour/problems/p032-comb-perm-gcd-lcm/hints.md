## Hint 1

`comb(n, k)` counts *groups* (A-B is the same handshake as B-A); `perm(n, k)` counts *ordered
arrangements* (gold-Asha/silver-Ben differs from gold-Ben/silver-Asha). Which question is which?
For the buses, is the product of the intervals the *first* common time?

## Hint 2

`math.gcd(3, -9)` is `3` (always non-negative). After dividing both parts by it, how do you make
sure the denominator is positive? For squares, `math.sqrt` returns a float with about 16 digits;
what does `math.isqrt(n)` return?

## Hint 3

```
handshakes:        comb(n, 2)
podium_orders:     perm(n, k)
simplify:          if den == 0: raise ZeroDivisionError
                   g = gcd(num, den); num //= g; den //= g
                   if den < 0: num, den = -num, -den
first_common_time: validate; return lcm(*intervals)
is_perfect_square: if n < 0: False;  r = isqrt(n);  return r * r == n
```
