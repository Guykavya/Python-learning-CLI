# An endless stream of primes

A prime is a whole number greater than 1 that can be divided evenly only by 1 and itself:
2, 3, 5, 7, 11, 13, ...

The classic "sieve" needs to know the upper limit in advance. A generator does not: it can produce
primes for ever, and the caller decides how many to take. Write in `solution.py`:

1. `primes()`: an **infinite** generator of primes in increasing order: 2, 3, 5, 7, ...
2. `nth_prime(n)`: the n-th prime, counting from 1 (`nth_prime(1) == 2`). Raise `ValueError` if
   `n < 1`. Use `primes()` and `itertools.islice`; do not write a second prime test.
3. `primes_between(low, high)`: a **list** of the primes `p` with `low <= p < high`. Use
   `primes()` with `itertools.dropwhile` / `itertools.takewhile` (or an equivalent lazy loop
   that stops); the stream is infinite, so you must stop by yourself.
4. `twin_primes()`: an infinite generator of pairs `(p, p + 2)` where both are prime:
   `(3, 5), (5, 7), (11, 13), (17, 19), ...`

It must be fast enough to find `nth_prime(2000)` (which is 17389) in well under a second.

**Examples**

```python
list(itertools.islice(primes(), 6))          # [2, 3, 5, 7, 11, 13]
nth_prime(5)                                 # 11
primes_between(10, 30)                       # [11, 13, 17, 19, 23, 29]
list(itertools.islice(twin_primes(), 3))     # [(3, 5), (5, 7), (11, 13)]
```

**Speed tip.** To test if `n` is prime, it is enough to try dividing by the primes you have
already found, and only those with `p * p <= n`.
