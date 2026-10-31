from dataclasses import InitVar, dataclass, field


@dataclass
class Account:
    owner: str
    balance: float = 0.0
    history: list = field(default_factory=list, init=False)

    def __post_init__(self):
        if not isinstance(self.owner, str) or not self.owner.strip():
            raise ValueError("owner must be a non-empty string")
        if self.balance < 0:
            raise ValueError("balance cannot be negative")
        self.owner = self.owner.strip().title()
        self.history.append(("open", self.balance))


@dataclass(frozen=True)
class Range:
    low: int
    high: int
    step: int = 1

    def __post_init__(self):
        if self.step <= 0:
            raise ValueError("step must be positive")
        if self.low > self.high:
            raise ValueError("low must not be greater than high")

    def values(self):
        return list(range(self.low, self.high + 1, self.step))


@dataclass
class Rectangle:
    width: float
    height: float
    unit_scale: InitVar[float] = 1.0
    area: float = field(init=False)

    def __post_init__(self, unit_scale):
        self.width *= unit_scale
        self.height *= unit_scale
        self.area = self.width * self.height
