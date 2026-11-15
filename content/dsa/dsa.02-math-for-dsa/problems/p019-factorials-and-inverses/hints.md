## Hint 1

You may not compute `fact[n] // (fact[r] * fact[n-r])` using remainders: dividing remainders does not give the remainder of
the true quotient. What replaces "divide by x" when working modulo a prime?

## Hint 2

Multiply by the modular inverse `x^(p-2) mod p`. Computing one inverse per query is slow-ish. Can you compute the inverse of `N!`
once, and get the inverse of every smaller factorial from it? (`1/(i-1)! = i * (1/i!)`.)

## Hint 3

```
MOD = 10**9 + 7
fact[0] = 1; fact[i] = fact[i-1] * i % MOD
inv_fact[N] = pow(fact[N], MOD - 2, MOD)
for i from N down to 1: inv_fact[i-1] = inv_fact[i] * i % MOD
answer = fact[n] * inv_fact[r] % MOD * inv_fact[n-r] % MOD    (0 if r > n)
```
