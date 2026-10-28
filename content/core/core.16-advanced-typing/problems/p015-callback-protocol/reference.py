from collections.abc import Iterable
from typing import Protocol


class Formatter(Protocol):
    def __call__(self, value: float, *, precision: int = 2) -> str: ...


def fixed(value: float, *, precision: int = 2) -> str:
    return f"{value:.{precision}f}"


def percent(value: float, *, precision: int = 2) -> str:
    return f"{value * 100:.{precision}f}%"


def format_all(values: Iterable[float], fmt: Formatter, precision: int = 2) -> list[str]:
    return [fmt(v, precision=precision) for v in values]
