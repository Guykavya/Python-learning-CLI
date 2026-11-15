## Hint 1

Take `n = 13`, `r = 6`. Then `13!` is bigger than `10^9 + 7`, so `fact[13]` is a **remainder**, not the real factorial.
Is `fact[13] // (fact[6] * fact[7])` the same as the remainder of the real answer? Try it and compare with
`math.comb(13, 6) % MOD`.

## Hint 2

Division does not survive taking remainders. In arithmetic modulo a prime `p`, "dividing by `x`" means multiplying by the
**inverse** of `x`, which is `x^(p-2) % p`. Build the denominator first: `d = fact[r] * fact[n - r] % MOD`.

## Hint 3

Bug 2: `fact = [1] * MAXN` has indices `0..MAXN - 1`, but `n` can be `MAXN`. Make the list one longer and run the loop to
`MAXN` inclusive. Bug 3: for `r > n`, `n - r` is negative and `fact[n - r]` reads from the end of the list. Check
`r > n` first and print 0.

```
if r > n: print 0
else:
    d = fact[r] * fact[n - r] % MOD
    print fact[n] * pow(d, MOD - 2, MOD) % MOD
```
