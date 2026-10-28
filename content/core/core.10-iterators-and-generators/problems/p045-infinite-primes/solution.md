## Approach

`primes()` is an infinite `while True` loop that tests each number with the primes it has already
found. A divisor larger than `sqrt(n)` always has a partner smaller than `sqrt(n)`, so we stop at
`p * p > n`. The other three functions never test numbers themselves; they only **cut** the
infinite stream: `islice` by position, `dropwhile`/`takewhile` by value, and a "previous" variable
to look at neighbours.

## Code

```python
import itertools
from collections.abc import Iterator


def primes() -> Iterator[int]:
    found: list[int] = []
    n = 2
    while True:
        is_prime = True
        for p in found:
            if p * p > n:
                break
            if n % p == 0:
                is_prime = False
                break
        if is_prime:
            found.append(n)
            yield n
        n += 1


def nth_prime(n: int) -> int:
    if n < 1:
        raise ValueError(f"n must be at least 1, got {n}")
    return next(itertools.islice(primes(), n - 1, None))


def primes_between(low: int, high: int) -> list[int]:
    big_enough = itertools.dropwhile(lambda p: p < low, primes())
    return list(itertools.takewhile(lambda p: p < high, big_enough))


def twin_primes() -> Iterator[tuple[int, int]]:
    previous = None
    for p in primes():
        if previous is not None and p - previous == 2:
            yield previous, p
        previous = p
```

Note the `ValueError` check comes **before** any generator work. `nth_prime` is a normal function,
so the error is raised at once.

## Complexity

Testing `n` costs about the number of primes up to `sqrt(n)`. Memory: the list of primes found so far.

## Another way

The incremental sieve uses a **dict** that maps each upcoming composite number to the primes that
"hit" it:

```python
def primes():
    hits = {}                      # composite -> list of primes that divide it
    n = 2
    while True:
        if n not in hits:
            yield n                # nobody hit n: it is prime
            hits[n * n] = [n]      # its first composite worth marking
        else:
            for p in hits.pop(n):  # move each prime to its next multiple
                hits.setdefault(n + p, []).append(p)
        n += 1
```

It does no division at all and is faster for large counts, at the cost of a trickier idea.
