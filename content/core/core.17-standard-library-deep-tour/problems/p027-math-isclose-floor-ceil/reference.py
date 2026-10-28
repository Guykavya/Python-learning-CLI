import math


def floor_ceil_trunc(x: float) -> tuple[int, int, int]:
    return math.floor(x), math.ceil(x), math.trunc(x)


def pages_needed(n_items: int, per_page: int) -> int:
    if per_page <= 0 or n_items < 0:
        raise ValueError("per_page must be positive and n_items not negative")
    return -(-n_items // per_page)


def round_down_to(x: float, step: float) -> float:
    if step <= 0:
        raise ValueError("step must be positive")
    return math.floor(x / step) * step


def close_enough(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
