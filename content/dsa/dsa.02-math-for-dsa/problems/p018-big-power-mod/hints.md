## Hint 1

If you already know `a^x mod m`, what is `a^(10x + d) mod m` in terms of it? Use `a^(10x + d) = (a^x)^10 * a^d`.

## Hint 2

Start with `r = 1 % m` (this is `a^0`). Read the characters of `b` one at a time. For each digit `d`, update
`r = (r^10 mod m) * (a^d mod m) mod m`. Each update costs two small modular powers.

## Hint 3

```
r = 1 % m
for ch in b_string:
    d = int(ch)
    r = pow(r, 10, m) * pow(a, d, m) % m
print r
```

If `m` is prime, you may also reduce `b mod (m - 1)` (Fermat), but only when `gcd(a, m) = 1`.
