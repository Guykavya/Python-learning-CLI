## Hint 1

For one `n`, what do you try first? Take `p` = 2, 3, 5, ... and ask: is `n - p` also prime? Stop at the first success. You will
usually stop very early.

## Hint 2

The loop is short. The expensive part is the primality test. If each test costs about `sqrt(n)` steps and you have
3000 queries, you pay for it again and again. Could a table answer "is `x` prime?" in one step?

## Hint 3

```
sieve = primality table up to 10^6          # build once
for each query n:
    p = 2
    while not (is_prime[p] and is_prime[n - p]):
        p += 1
    print(p, n - p)
```
