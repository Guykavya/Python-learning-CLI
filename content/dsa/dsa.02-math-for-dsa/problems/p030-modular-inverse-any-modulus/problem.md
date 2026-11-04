# Modular inverse for any modulus

For each query `a m`, print the smallest non-negative `x` with `a * x % m == 1`, or `-1` if no such `x` exists.

Remember: the inverse exists exactly when `gcd(a, m) = 1`. The modulus may be **composite** and as large as
`10^18`, so Fermat's `a^(m-2)` is not allowed, and a loop over `x = 1..m-1` is far too slow. Use extended Euclid.

## Input

- Line 1: `q`.
- Then `q` lines, each with `a` and `m`.

## Output

For each query, one line: the inverse in `0..m-1`, or `-1`.

## Example

Input:

```
5
3 10
4 10
10 17
-3 7
5 1
```

Output:

```
7
-1
12
2
0
```

`3 * 7 = 21 = 2*10 + 1`. `gcd(4, 10) = 2`, so no inverse. `10 * 12 = 120 = 7*17 + 1`. `-3 = 4 (mod 7)` and `4 * 2 = 8 = 1`
(mod 7). For `m = 1` every number is 0, and `0 * 0 % 1 = 0 = 1 % 1`, so the answer is 0.

## Constraints

- `1 <= q <= 20000`
- `-10^18 <= a <= 10^18`, `1 <= m <= 10^18`

Use `input()` without a prompt message. You may use the extended Euclid function from the previous problem.
Python's `%` always gives a non-negative result for a positive modulus, which helps with negative `a`.
