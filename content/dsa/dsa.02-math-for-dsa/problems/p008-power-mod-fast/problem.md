# Fast power modulo m

Compute `a^b mod m` where the exponent `b` can be as large as 10^18. Multiplying `a` by itself `b` times
needs 10^18 steps, and `a ** b` would have trillions of digits. Use **binary exponentiation**:

- if `b` is odd, multiply the result by `a` (reducing mod `m`);
- then square `a` (mod `m`) and halve `b`;
- repeat until `b` is 0.

This needs only about 60 steps. Write the loop yourself; do not use `pow(a, b, m)` (the built-in does exactly
this, and you are here to learn how).

Why the modulus, when Python has no overflow? Contest answers are asked "modulo 10^9 + 7" so that they
fit a 64-bit integer in C++ and Java. In Python the same habit keeps numbers small and fast: reducing after
each multiplication keeps every number below `m * m`.

## Input

- Line 1: `q`.
- The next `q` lines: three integers `a b m`.

## Output

`q` lines: `a^b mod m` for each query.

## Example

Input:

```
3
2 10 1000
3 0 7
5 3 1
```

Output:

```
24
1
0
```

`2^10 = 1024`, mod 1000 gives 24. Anything to the power 0 is 1 (here `1 mod 7 = 1`). Everything is 0 mod 1.

## Constraints

- `1 <= q <= 1000`
- `0 <= a <= 10^9`, `0 <= b <= 10^18`, `1 <= m <= 10^9 + 7`

Use `input()` without a prompt message.
