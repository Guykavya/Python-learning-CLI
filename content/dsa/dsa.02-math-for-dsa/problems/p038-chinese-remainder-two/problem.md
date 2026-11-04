# Two congruences at once

For each query `a1 m1 a2 m2`, find the smallest `x >= 0` with

```
x = a1 (mod m1)
x = a2 (mod m2)
```

or print `-1` if there is none. The moduli need **not** be coprime.

## Method

Write `x = a1 + m1 * k`. The second congruence becomes `m1 * k = a2 - a1 (mod m2)`: a linear congruence (see the
earlier problem). Let `g = gcd(m1, m2)`.

- It has a solution only if `g` divides `a2 - a1`.
- Then `k = ((a2 - a1) / g) * inverse(m1 / g, m2 / g) mod (m2 / g)`.
- Then `x = a1 + m1 * k`, and all solutions are `x + t * lcm(m1, m2)`. With `0 <= a1 < m1` and `0 <= k < m2 / g`, this `x` is already below the lcm, so it is the smallest one.

## Input

- Line 1: `q`.
- Then `q` lines, each with `a1 m1 a2 m2`.

## Output

For each query, the smallest non-negative `x`, or `-1`.

## Example

Input:

```
4
2 3 3 5
1 4 3 6
1 4 2 6
5 12 5 18
```

Output:

```
8
9
-1
5
```

`8 = 2 (mod 3)` and `8 = 3 (mod 5)`. For `1 4 3 6`: `9 = 1 (mod 4)` and `9 = 3 (mod 6)`; the next one would be `9 + 12`.
For `1 4 2 6`: `x` would be odd (1 mod 4) and even (2 mod 6): impossible. For `5 12 5 18`: `x = 5` itself works, and the lcm is 36.

## Constraints

- `1 <= q <= 10000`
- `1 <= m1, m2 <= 10^9`, `0 <= a1 < m1`, `0 <= a2 < m2`

Use `input()` without a prompt message. The answer can be up to about `10^18`.
