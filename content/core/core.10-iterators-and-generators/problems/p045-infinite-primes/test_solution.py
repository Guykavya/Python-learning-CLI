import itertools
import time

import pytest

from solution import nth_prime, primes, primes_between, twin_primes


def test_first_primes():
    assert list(itertools.islice(primes(), 10)) == [2, 3, 5, 7, 11, 13, 17, 19, 23, 29], (
        "The first ten primes. 1 is not prime; 2 is the only even prime; 9, 15, 21, 25, 27 are not prime."
    )


def test_primes_is_infinite_and_lazy():
    g = primes()
    assert iter(g) is g, "primes() must return a generator, not a list."
    got = list(itertools.islice(g, 3))
    assert got == [2, 3, 5], "Take items one by one with islice."
    assert next(g) == 7, "The generator must continue where it stopped."


def test_squares_of_primes_not_prime():
    first = set(itertools.islice(primes(), 100))
    for square in (4, 9, 25, 49, 121, 169):
        assert square not in first, f"{square} is a square of a prime. Use p * p <= n (not <) when you stop trying divisors."


def test_nth_prime():
    assert nth_prime(1) == 2, "Counting starts at 1: nth_prime(1) is 2."
    assert nth_prime(5) == 11, "The 5th prime is 11. Check for an off-by-one in islice."
    assert nth_prime(100) == 541, "The 100th prime is 541."


def test_nth_prime_bad_input():
    with pytest.raises(ValueError):
        nth_prime(0)
    with pytest.raises(ValueError):
        nth_prime(-3)


def test_speed():
    start = time.perf_counter()
    assert nth_prime(2000) == 17389, "The 2000th prime is 17389."
    assert time.perf_counter() - start < 2, (
        "Too slow. Only divide by primes found so far, and stop when p * p > n."
    )


def test_primes_between():
    assert primes_between(10, 30) == [11, 13, 17, 19, 23, 29], "low is included, high is not."
    assert primes_between(2, 3) == [2], "low is included."
    assert primes_between(14, 17) == [], "No primes in 14, 15, 16. high is not included."
    assert primes_between(0, 10) == [2, 3, 5, 7], "Numbers below 2 are not prime."


def test_primes_between_returns_list():
    assert isinstance(primes_between(1, 20), list), "primes_between returns a list."


def test_twin_primes():
    got = list(itertools.islice(twin_primes(), 6))
    assert got == [(3, 5), (5, 7), (11, 13), (17, 19), (29, 31), (41, 43)], (
        "Pairs of primes that differ by 2. 5 belongs to two pairs. Remember the previous prime as you go."
    )
