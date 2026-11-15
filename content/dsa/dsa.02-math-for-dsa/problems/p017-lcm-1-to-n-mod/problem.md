# LCM of 1..n, modulo 10^9 + 7

`lcm(1, 2, ..., n)` grows very fast: `lcm(1..20) = 232792560`, and `lcm(1..10^6)` has about 430000 digits. Print it
modulo `10^9 + 7`.

Folding with `lcm(a, b) = a // gcd(a, b) * b` over 10^6 numbers works in principle, but the number keeps growing
to 1.4 million bits, and every step touches all of it. Too slow. Use prime factors instead:

> For each prime `p <= n`, the lcm contains `p^k` where `p^k` is the **largest power of `p` that is `<= n`**.
> Multiply those powers together, taking the remainder after each multiplication.

Why: the lcm has, for every prime, the **largest exponent** found in any of the numbers `1..n`. The biggest
power of `p` among them is the largest `p^k <= n`.

## Input

One line: `n`.

## Output

One line: `lcm(1..n) mod 1000000007`.

## Example

Input:

```
10
```

Output:

```
2520
```

`2^3 * 3^2 * 5 * 7 = 8 * 9 * 5 * 7 = 2520`.

## Constraints

- `1 <= n <= 10^6`
- The modulus is `10^9 + 7`. Python does not overflow, but a number with 430000 digits is slow to multiply.
  Taking `% 1000000007` after each multiplication keeps every number small. (In C++ or Java it would also
  be needed to avoid overflow.)

Use `input()` without a prompt message.
