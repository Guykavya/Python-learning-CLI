## Hint 1

`primes()` can keep a list of the primes it has already yielded. For the next number `n`, which
numbers do you need to try as divisors? When can you stop trying?

## Hint 2

`nth_prime(n)`: `islice(primes(), n - 1, None)` skips the first `n - 1` primes; `next()` of it is
the one you want.

`primes_between`: first skip the small ones with `dropwhile(lambda p: p < low, ...)`, then take
while `p < high`. `takewhile` stops at the first prime that is too big, so the infinite stream ends.

## Hint 3

```
primes():
    found = []
    n = 2
    loop for ever:
        if no p in found with p * p <= n divides n:
            found.append(n); yield n
        n += 1

twin_primes():
    previous = None
    for p in primes():
        if previous is not None and p - previous == 2: yield (previous, p)
        previous = p
```
