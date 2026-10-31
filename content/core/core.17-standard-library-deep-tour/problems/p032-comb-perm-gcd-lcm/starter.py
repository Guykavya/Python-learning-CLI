import math


def handshakes(n: int) -> int:
    """How many handshakes when each of n people shakes hands once with every other."""
    return n * n


def podium_orders(n: int, k: int = 3) -> int:
    """Ordered podiums (1st, 2nd, 3rd, ...) of k places from n runners."""
    return n * k


def simplify(num: int, den: int) -> tuple[int, int]:
    """The fraction num/den in lowest terms, sign on the numerator."""
    return num, den


def first_common_time(intervals: list[int]) -> int:
    """Buses leave together at minute 0 and then every intervals[i] minutes. When together again?"""
    result = 1
    for i in intervals:
        result *= i
    return result


def is_perfect_square(n: int) -> bool:
    """True if n is k*k for some integer k."""
    return n >= 0 and int(math.sqrt(n)) ** 2 == n
