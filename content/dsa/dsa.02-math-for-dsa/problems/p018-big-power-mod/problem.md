# Power with a huge exponent

Compute `a^b mod m` where the exponent `b` is given as a **decimal string with up to 100000 digits**.

Two traps wait here:

1. Python refuses to turn a string of more than 4300 digits into an `int` (`ValueError: Exceeds the limit`),
   unless you change the limit with `sys.set_int_max_str_digits(0)`.
2. You cannot replace `b` by `b % m`. The exponent is reduced modulo something else (see below), not modulo `m`.

A clean way that avoids both: **process the digits of `b` from left to right**. Let `b = d1 d2 ... dk` in decimal.
If `r` is `a^(prefix)` for the digits read so far, then appending a digit `d` changes the exponent from `x` to `10x + d`,
so the new value is `a^(10x + d) = (a^x)^10 * a^d`. In code: `r = pow(r, 10, m) * pow(a, d, m) % m`
(the built-in three-argument `pow` is fine here, you already wrote it by hand in an earlier problem).

## Input

- Line 1: `a`.
- Line 2: `b`, as a string of decimal digits (no leading zeros, except the single digit `0`).
- Line 3: `m`.

## Output

One line: `a^b mod m`.

## Example

Input:

```
2
100
7
```

Output:

```
2
```

`2^100 mod 7`: the powers of 2 mod 7 repeat 2, 4, 1, 2, 4, 1, ... (period 3), and `100 mod 3 = 1`, so the answer is 2.
(`b mod m = 100 mod 7 = 2` would give `2^2 = 4`: wrong.)

## Constraints

- `0 <= a <= 10^9`, `1 <= m <= 10^9 + 7` (`m` is not necessarily prime)
- `b` has between 1 and 100000 digits

Use `input()` without a prompt message.
