## Hint 1

Fermat: for prime `p` and `b` not divisible by `p`, `b ** (p - 1) ≡ 1`. What does that make `b ** (p - 2)`?

## Hint 2

`pow(b, p - 2, p)` computes `b ** (p - 2) mod p` in `O(log p)` steps without building the huge number. Python 3.8+ also accepts `pow(b, -1, p)`. Reduce `b % p` first to check whether the inverse exists.

## Hint 3

```text
for each query:
    if b % p == 0: print -1
    else: print a % p * pow(b, p - 2, p) % p
```
