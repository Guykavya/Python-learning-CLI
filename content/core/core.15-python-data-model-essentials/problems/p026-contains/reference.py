class Interval:
    def __init__(self, lo, hi):
        self.lo = lo
        self.hi = hi

    def __contains__(self, item):
        if not isinstance(item, (int, float)):
            return False
        return self.lo <= item <= self.hi


class WordSet:
    def __init__(self, words):
        self._words = {w.casefold() for w in words}

    def __contains__(self, item):
        if not isinstance(item, str):
            return False
        return item.casefold() in self._words
