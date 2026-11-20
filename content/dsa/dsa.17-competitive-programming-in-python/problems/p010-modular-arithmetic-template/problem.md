# Modular arithmetic template

Contest answers are often asked "modulo a prime `p`". Division is then done with the **modular inverse**.

For each query `a b p` (`p` is prime) print `a / b mod p`: the number `x` with `0 <= x < p` such that `x * b ≡ a (mod p)`. If `b` is divisible by `p`, there is no inverse and you print `-1`.

## Input

The first line holds `t` (`1 <= t <= 10**5`). Each of the next `t` lines holds `a b p` (`0 <= a, b <= 10**18`, `2 <= p <= 10**9 + 7`, `p` prime).

## Output

One answer per line.

## Example

```text
3
1000000000000 6 1000000007
6 3 7
10 7 7
```
```text
333332169
2
-1
```

`6 / 3 mod 7`: the inverse of 3 mod 7 is 5 (`3 * 5 = 15 ≡ 1`), so `6 * 5 = 30 ≡ 2`. In the last query `7` is divisible by `p = 7`.

## The catch

Looping `x = 0, 1, 2, ...` until `x * b % p == a % p` takes up to `p` steps, which is `10**9`. Use Fermat's little theorem or the three-argument `pow` (chapter section 11).
