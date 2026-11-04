## Hint 1

List `6x % 10` for `x = 0..9`. Which values appear? Which values of `b` can you reach? What do they have in common with
`gcd(6, 10)`?

## Hint 2

Once you divide `a`, `b`, and `m` by `g`, does `a'` have an inverse modulo `m'`? What does that give you?

## Hint 3

If `x0` is a solution modulo `m'`, then `x0 + m'` is also a solution modulo `m` (adding `m'` changes `a x` by `a m'`, a
multiple of `m`). How many times can you add `m'` before reaching `m`?
