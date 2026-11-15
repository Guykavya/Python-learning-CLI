**1. Condition.** `a` has an inverse modulo `m` if and only if `gcd(a, m) = 1` (they are *coprime*). Example: `a = 3`,
`m = 10`: `3 * 7 = 21`, and `21 % 10 = 1`, so the inverse is 7. For `a = 4`, `m = 10` the products `4*x % 10` for
`x = 0..9` are 0, 4, 8, 2, 6, 0, 4, 8, 2, 6. The value 1 never appears: no inverse.

**2. Why.** If `d = gcd(a, m) > 1`, then `d` divides `a * x` for every `x`, and `d` also divides `m`. So `a * x`
modulo `m` is always a multiple of `d`: `a * x = k * m + r` gives `r = a * x - k * m`, which `d` divides. The remainder
`r` can never be 1, because 1 is not a multiple of `d`. (For `a = 4`, `m = 10`, the remainders are all even.)

**3. Fermat.** Fermat's little theorem says `a^(m-1) = 1 (mod m)` only when `m` is **prime** and `m` does not divide
`a`. Then `a * a^(m-2) = 1`, so `a^(m-2)` is the inverse. For a composite `m` the theorem does not apply. Example:
`a = 3`, `m = 10`: `3^8 = 6561`, and `6561 % 10 = 1`, which happens to work here, but `a = 5`, `m = 12`... use
`a = 2`, `m = 9` (inverse 5 since `2 * 5 = 10`): `2^7 = 128`, `128 % 9 = 2`, which is wrong. The formula silently gives
garbage, with no error.

**4. Extended Euclid.** It finds integers `x, y` with `a*x + b*y = gcd(a, b)`. Call it with `b = m`:
`a*x + m*y = g`. If `g = 1`, then taking this modulo `m` gives `a*x = 1 (mod m)`, so `x % m` is the inverse. If `g > 1`,
there is no inverse. It works for **any** `m`, prime or not, and it also tells you when no inverse exists.

**5. Choose.**
(a) Modulo `10^9 + 7` (a prime) with many queries: Fermat with fast exponentiation, or better, compute the inverse
factorials once and reuse them. Both are about 30 multiplications per inverse.
(b) A modulus that may be composite, or may be huge: extended Euclid. It is O(log m) and also detects "no inverse".
(c) Modulus 1: every number is 0 modulo 1, and `0 * x % 1 = 0 = 1 % 1`, so the inverse is 0. Extended Euclid gives
that without a special case.

**Common traps.** Using Fermat with a composite modulus. Forgetting that `a = 0` has no inverse (`gcd(0, m) = m`, which
is 1 only for `m = 1`). Returning a negative `x` from extended Euclid; always reduce with `x % m`.
