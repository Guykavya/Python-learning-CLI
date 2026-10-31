## Approach

Enum classes are classes whose assigned names become **singleton members**. `auto()` asks the enum to pick the values: 1, 2, 3, ... for a plain `Enum`. Lookup by name (`cls[...]`) and by value (`cls(...)`) are built in, so a `from_name` classmethod only cleans the text and translates the error. Methods are normal methods; the dict inside `opposite()` is a lookup table from member to member.

## Code

```python
from enum import Enum, auto


class Weekday(Enum):
    MON = auto()
    TUE = auto()
    WED = auto()
    THU = auto()
    FRI = auto()
    SAT = auto()
    SUN = auto()

    @property
    def is_weekend(self):
        return self in (Weekday.SAT, Weekday.SUN)

    @classmethod
    def from_name(cls, text):
        key = text.strip().upper()[:3]
        try:
            return cls[key]
        except KeyError:
            raise ValueError(f"not a weekday: {text!r}") from None

    def next(self):
        members = list(type(self))
        return members[(members.index(self) + 1) % len(members)]


class Direction(Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"

    def opposite(self):
        return {Direction.NORTH: Direction.SOUTH, Direction.SOUTH: Direction.NORTH,
                Direction.EAST: Direction.WEST, Direction.WEST: Direction.EAST}[self]
```

## Complexity

`next()` is O(n) with `list.index` for n = 7; a lookup is O(1).

## Another way

Define `next` with `Weekday((self.value % 7) + 1)`: shorter, but it relies on the values being 1..7. The member-list version keeps working if you add or reorder members.
