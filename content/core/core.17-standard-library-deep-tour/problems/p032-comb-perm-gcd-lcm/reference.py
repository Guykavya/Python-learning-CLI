import math


def handshakes(n: int) -> int:
    return math.comb(n, 2)


def podium_orders(n: int, k: int = 3) -> int:
    return math.perm(n, k)


def simplify(num: int, den: int) -> tuple[int, int]:
    if den == 0:
        raise ZeroDivisionError("the denominator is 0")
    g = math.gcd(num, den)
    num, den = num // g, den // g
    if den < 0:
        num, den = -num, -den
    return num, den


def first_common_time(intervals: list[int]) -> int:
    if not intervals or any(i <= 0 for i in intervals):
        raise ValueError("intervals must be positive and not empty")
    return math.lcm(*intervals)


def is_perfect_square(n: int) -> bool:
    if n < 0:
        return False
    r = math.isqrt(n)
    return r * r == n
