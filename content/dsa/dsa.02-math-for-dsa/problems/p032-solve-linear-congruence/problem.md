# Solve `a x = b (mod m)`

For each query `a b m`, print the smallest `x` with `0 <= x < m` and `a * x % m == b % m`, or `-1` if there is none.

Recall the facts (see the explain problem): let `g = gcd(a, m)`. There is a solution if and only if `g` divides `b`. Then,
dividing by `g`, the congruence `(a/g) x = (b/g) (mod m/g)` has exactly one solution modulo `m/g`, and it is the smallest
non-negative answer.

## Input

- Line 1: `q`.
- Then `q` lines, each with `a`, `b`, `m`.

## Output

For each query, the smallest solution, or `-1`.

## Example

Input:

```
5
6 4 10
4 3 8
3 1 7
0 0 5
7 3 1
```

Output:

```
4
-1
5
0
0
```

`6*4 = 24 = 4 (mod 10)`, and `x = 4` is the smaller of 4 and 9. `4x % 8` is 0 or 4, never 3. `3*5 = 15 = 1 (mod 7)`.
`0*x = 0` for every `x`, so the smallest is 0. Modulo 1 everything is 0, so `x = 0` works.

## Constraints

- `1 <= q <= 20000`
- `-10^18 <= a, b <= 10^18`, `1 <= m <= 10^18`

Use `input()` without a prompt message. Use the extended Euclid method for inverses (Python's `pow(a, -1, m)` also exists,
but the point of this problem is that `a` and `m` are **not** coprime in general).
