# LCM of two numbers

The **least common multiple** `lcm(a, b)` is the smallest positive number that both `a` and `b` divide.
For example `lcm(4, 6) = 12`.

It is linked to the gcd by `gcd(a, b) * lcm(a, b) = a * b`, so `lcm(a, b) = a // gcd(a, b) * b`.
Divide **first**, then multiply: the intermediate number stays smaller. In C++ or Java, `a * b` for
`a, b` near 10^18 overflows a 64-bit integer even when the lcm fits. Python integers never overflow,
but the habit of dividing first is still worth having, because big integers are slower.

Use Euclid's loop for the gcd.

## Input

- Line 1: `q`.
- The next `q` lines: two integers `a b`.

## Output

`q` lines: `lcm(a, b)` for each pair, as an exact integer (no decimal point, no `e+`).

## Example

Input:

```
3
4 6
7 5
10 10
```

Output:

```
12
35
10
```

## Constraints

- `1 <= q <= 1000`
- `1 <= a, b <= 10^18` (the answer can have 36 digits)

Use `input()` without a prompt message.
