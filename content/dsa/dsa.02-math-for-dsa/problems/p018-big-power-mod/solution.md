## Approach

Reading the digits left to right, the exponent after each digit is `10 * x + d`. Since `a^(10x + d) = (a^x)^10 * a^d`, we can keep
`r = a^x mod m` and update it with two small modular powers. We never build the huge exponent and never convert the string to an `int`.

## Code

```python
a = int(input())
b = input().strip()
m = int(input())

r = 1 % m
for ch in b:
    d = int(ch)
    r = pow(r, 10, m) * pow(a, d, m) % m
print(r)
```

## Complexity

O(k) updates for `k` digits, each with two modular powers of tiny exponents: about 10^5 * a few dozen multiplications. A fraction of a second.

## Another way

1. `sys.set_int_max_str_digits(0)`, then `pow(a, int(b), m)`. The built-in handles a 330000-bit exponent in about 330000 squarings.
2. If `m` is prime and `a % m != 0`, Fermat's little theorem says `a^(m-1) = 1 (mod m)`, so the exponent can be reduced:
   `a^b = a^(b mod (m - 1))`. Computing `b mod (m - 1)` from the string is done digit by digit too: `t = (t * 10 + d) % (m - 1)`.
   For a general `m` the period is the Euler totient `phi(m)`, which needs the factorisation of `m`.
