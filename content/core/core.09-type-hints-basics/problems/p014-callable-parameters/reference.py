from collections.abc import Callable


def apply_all(func: Callable[[int], int], numbers: list[int]) -> list[int]:
    return [func(n) for n in numbers]


def keep_if(test: Callable[[int], bool], numbers: list[int]) -> list[int]:
    return [n for n in numbers if test(n)]


def compose(first: Callable[[int], int], second: Callable[[int], int]) -> Callable[[int], int]:
    def both(x: int) -> int:
        return second(first(x))

    return both


def make_adder(n: int) -> Callable[[int], int]:
    def add(x: int) -> int:
        return x + n

    return add
