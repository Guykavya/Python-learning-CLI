# GCD with Euclid's algorithm

The **greatest common divisor** `gcd(a, b)` is the largest number that divides both `a` and `b`.
For example `gcd(12, 18) = 6`. By convention `gcd(a, 0) = a` and `gcd(0, 0) = 0`.

Write it yourself, without `math.gcd`, with **Euclid's algorithm**: replace `(a, b)` by `(b, a % b)` until
`b` is 0. Then `a` is the answer.

Why it works: any number that divides both `a` and `b` also divides `a % b` (which is `a` minus some multiple of
`b`), and the other way round. So the pair `(b, a % b)` has the same common divisors as `(a, b)`, but smaller numbers.

## Input

- Line 1: `q`.
- The next `q` lines: two integers `a b`.

## Output

`q` lines: `gcd(a, b)` for each pair.

## Example

Input:

```
4
12 18
0 5
7 0
17 5
```

Output:

```
6
5
7
1
```

## Constraints

- `1 <= q <= 1000`
- `0 <= a, b <= 10^18`

Subtracting repeatedly, or trying every number downward from `min(a, b)`, is far too slow for numbers this big.
Euclid needs only about 90 steps even for 10^18.

Use `input()` without a prompt message.
