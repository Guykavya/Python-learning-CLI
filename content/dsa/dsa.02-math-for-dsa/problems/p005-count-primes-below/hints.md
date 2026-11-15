## Hint 1

If you sieve for each query separately, how much work is that in total? What changes between two queries: the
sieve, or only the number you look at?

## Hint 2

Sieve once up to `max(queries)`. Then you want "how many primes are `<= n`" for many `n`. If `count[k]` stores the
number of primes `<= k`, a query is one list lookup. How do you fill `count` from `is_prime` in a single pass?

## Hint 3

```
read all queries; top = max of them
sieve is_prime up to top
count[0] = 0
for k from 1 to top: count[k] = count[k-1] + (1 if is_prime[k] else 0)
for each query n: print count[n]
```
