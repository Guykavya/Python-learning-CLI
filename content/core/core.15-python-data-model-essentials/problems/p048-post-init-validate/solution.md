## Approach

The generated `__init__` is: assign every `init=True` field, set `init=False` fields to their defaults (or default factories), then call `__post_init__` (passing the `InitVar` values). So `__post_init__` sees a fully built object and can check it, normalise it, or compute more fields.

`Range` shows the frozen limitation: the checks work because they only read. A frozen dataclass that needs to *change* a field in `__post_init__` has to use `object.__setattr__(self, "name", value)`, which is rarely worth it.

## Code

```python
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
```

## Complexity

O(1) per construction.

## Another way

Property setters on a plain class validate every assignment, not only construction (see core.14). `dataclass` validation in `__post_init__` checks only when the object is built; a later `acc.balance = -5` is not caught, unless you also write a setter.
