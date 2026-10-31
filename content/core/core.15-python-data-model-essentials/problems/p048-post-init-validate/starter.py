from dataclasses import InitVar, dataclass, field


@dataclass
class Account:
    owner: str
    balance: float = 0.0


@dataclass(frozen=True)
class Range:
    low: int
    high: int
    step: int = 1


@dataclass
class Rectangle:
    width: float
    height: float
