## Hint 1

`C(n, r) = n! / (r! * (n - r)!)`. If you had all factorials mod `p` stored in a list, what is one query?

## Hint 2

Division mod `p` is multiplication by the inverse. Compute the inverse of **one** factorial, `pow(fact[N], p - 2, p)`, and walk downwards: `inv_fact[i - 1] = inv_fact[i] * i % p`.

## Hint 3

```text
N = largest n in the queries
fact[0] = 1; fact[i] = fact[i-1] * i % p
inv_fact[N] = pow(fact[N], p - 2, p)
inv_fact[i-1] = inv_fact[i] * i % p   (for i from N down to 1)
query: 0 if r > n else fact[n] * inv_fact[r] % p * inv_fact[n-r] % p
```
