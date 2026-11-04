**1. Condition.** Let `g = gcd(a, m)`. The congruence `a x = b (mod m)` has a solution if and only if `g` divides `b`.
Reason: `a x - b = k m`, so `b = a x - k m`, and `g` divides both `a x` and `k m`. Test: `6x = 4 (mod 10)`: `g = 2`,
and 2 divides 4, so there are solutions: `x = 4` works (`24 % 10 = 4`), and so does `x = 9` (`54 % 10 = 4`).
`4x = 3 (mod 8)`: `g = 4`, and 4 does not divide 3. Indeed `4x % 8` is only ever 0 or 4, never 3.

**2. Number of solutions.** If a solution exists, there are exactly `g` solutions in `0..m-1`, and they are spaced
`m / g` apart: `x0, x0 + m/g, x0 + 2m/g, ...`. For `6x = 4 (mod 10)`: `g = 2`, spacing 5, solutions 4 and 9.

**3. Solving.** Divide everything by `g`: `a' = a/g`, `b' = b/g`, `m' = m/g`. Now `gcd(a', m') = 1`, so `a'` has an
inverse modulo `m'`, and `a' x = b' (mod m')` has exactly one solution modulo `m'`: `x0 = b' * inv(a') % m'`.
Example: `6x = 4 (mod 10)` becomes `3x = 2 (mod 5)`; `inv(3) = 2` modulo 5, so `x0 = 2 * 2 % 5 = 4`. The solutions modulo
10 are `4` and `4 + 5 = 9`. The smallest non-negative one is `x0` itself.

**4. Special cases.** If `g = 1`, there is always exactly one solution: `x = b * inv(a) % m`. If `a = 0`, then
`g = gcd(0, m) = m`, so a solution exists only if `m` divides `b`; then every `x` is a solution, and the smallest is 0.
If `m = 1`, everything is congruent to 0, so `x = 0` always works.

**5. Connection.** The modular inverse is the case `b = 1`: `a x = 1 (mod m)`. The condition "`g` divides 1" says
`g = 1`. It is the same rule, with a unique answer.

**Common trap.** Dividing both sides by `a` as if `m` were prime. When `gcd(a, m) > 1`, you must also divide the modulus.
