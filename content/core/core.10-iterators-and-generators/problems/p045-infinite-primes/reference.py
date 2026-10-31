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
