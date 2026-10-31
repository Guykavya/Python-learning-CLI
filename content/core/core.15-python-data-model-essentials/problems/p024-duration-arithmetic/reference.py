from functools import total_ordering


@total_ordering
class Duration:
    def __init__(self, seconds):
        if seconds < 0:
            raise ValueError("a Duration cannot be negative")
        self.seconds = seconds

    @classmethod
    def of(cls, hours=0, minutes=0, seconds=0):
        return cls(hours * 3600 + minutes * 60 + seconds)

    def __add__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(self.seconds + other.seconds)

    def __sub__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return Duration(self.seconds - other.seconds)

    def __mul__(self, n):
        if not isinstance(n, int):
            return NotImplemented
        return Duration(self.seconds * n)

    __rmul__ = __mul__

    def __floordiv__(self, n):
        if not isinstance(n, int):
            return NotImplemented
        return Duration(self.seconds // n)

    def __truediv__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return self.seconds / other.seconds

    def __eq__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return self.seconds == other.seconds

    def __lt__(self, other):
        if not isinstance(other, Duration):
            return NotImplemented
        return self.seconds < other.seconds

    def __hash__(self):
        return hash(self.seconds)

    def __str__(self):
        hours, rest = divmod(self.seconds, 3600)
        minutes, seconds = divmod(rest, 60)
        return f"{hours}:{minutes:02d}:{seconds:02d}"

    def __repr__(self):
        return f"Duration({self.seconds})"
