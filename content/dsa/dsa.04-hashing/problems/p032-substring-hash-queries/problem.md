# Substring hash queries

Define the **hash of a string** `t = t0 t1 ... t(k-1)` as

```
H(t) = (v(t0) * B^(k-1) + v(t1) * B^(k-2) + ... + v(t(k-1))) mod M
```

where `v('a') = 1, ..., v('z') = 26`, `B = 131` and `M = 1_000_000_007`. (This is the same value you get by starting
with `h = 0` and doing `h = (h * B + v) % M` for each letter.)

Given a string `s` and `q` queries `l r` (1-based, inclusive), print `H(s[l..r])` for each. Computing each hash from
scratch costs `O(r - l)` per query, too slow. Precompute **prefix hashes** once so that every query takes `O(1)`:

```
P[0] = 0,  P[i+1] = (P[i] * B + v(s[i])) % M
H(s[l..r]) = (P[r] - P[l-1] * B^(r-l+1)) % M       (1-based l, r)
```

## Input

- Line 1: the string `s`.
- Line 2: `q`.
- Next `q` lines: `l r`.

## Output

`q` lines, one hash each.

## Example

Input:

```
abcab
3
1 3
4 5
1 5
```

Output:

```
17426
133
299047719
```

By hand: `H("abc") = (1*131 + 2)*131 + 3 = 133*131 + 3 = 17426`, and `H("ab") = 1*131 + 2 = 133`. Two equal substrings (`"ab"`
at positions 1-2 and at 4-5) give the **same** hash. The third value is `H("abcab")` after reducing modulo `M`.

## Constraints

- `1 <= len(s), q <= 200000`
- `1 <= l <= r <= len(s)`
- Use `pow(B, e, M)` or a precomputed list of powers.
