from functools import total_ordering


@total_ordering
class Duration:
    def __init__(self, seconds):
        # TODO: ValueError for negative values
        self.seconds = seconds

    @classmethod
    def of(cls, hours=0, minutes=0, seconds=0):
        # TODO: build a Duration from the parts
        raise NotImplementedError

    # TODO: + - * // / ==  <  hash  str  repr
