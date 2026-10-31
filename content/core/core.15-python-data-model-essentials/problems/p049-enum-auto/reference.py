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
