from collections.abc import Callable


class Box[T]:
    def __init__(self, value: T) -> None:
        self.value = value

    def get(self) -> T:
        return self.value

    def map[U](self, func: Callable[[T], U]) -> "Box[U]":
        return Box(func(self.value))

    def __repr__(self) -> str:
        return f"Box({self.value!r})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Box):
            return NotImplemented
        return bool(self.value == other.value)

    def __hash__(self) -> int:
        return hash(("Box", self.value))


def biggest[N: (int, float)](a: N, b: N) -> N:
    return b if b > a else a
