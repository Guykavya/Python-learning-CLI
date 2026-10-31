import math


def floor_ceil_trunc(x: float) -> tuple[int, int, int]:
    """(floor, ceil, trunc) of x."""
    return int(x), int(x), int(x)


def pages_needed(n_items: int, per_page: int) -> int:
    """How many pages are needed to show n_items, per_page items on each page."""
    return n_items // per_page


def round_down_to(x: float, step: float) -> float:
    """The largest multiple of step that is <= x."""
    return int(x / step) * step


def close_enough(a: float, b: float) -> bool:
    """True if a and b are equal up to floating-point error."""
    return a == b
