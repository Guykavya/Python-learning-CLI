# Fix the nCr that divides

`starter.py` answers queries `n r`: print `C(n, r) % (10^9 + 7)`, and `0` when `r > n`. It looks right and it is quick, but it
has **three bugs**. It passes the first few tiny examples, so it is easy to believe it is correct. Find the bugs, explain to
yourself why each one is wrong, and fix them. Do not rewrite from scratch.

Hints about where to look, without saying what is wrong:

1. What does `//` do to numbers that are **already remainders**?
2. How many entries does `fact` have, and which `n` does the largest query use?
3. What happens in Python when an index is negative?

## Input

- Line 1: `q`.
- Then `q` lines, each with `n` and `r`.

## Output

For each query, one line: `C(n, r) % 1000000007`.

## Example

Input:

```
4
5 2
10 0
6 6
3 5
```

Output:

```
10
1
1
0
```

## Constraints

- `1 <= q <= 100000`
- `0 <= n <= 10^6`, `0 <= r <= 10^6`

Use `input()` without a prompt message. Python's built-in `pow(x, MOD - 2, MOD)` is allowed here: it is fast
exponentiation with a modulus, and for a prime modulus it gives the inverse of `x` (Fermat's little theorem).
