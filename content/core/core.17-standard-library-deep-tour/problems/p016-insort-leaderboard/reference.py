from bisect import bisect_left, bisect_right, insort


def _first(entry: tuple[int, str]) -> int:
    return entry[0]


class Leaderboard:
    def __init__(self) -> None:
        self._entries: list[tuple[int, str]] = []
        self._scores: dict[str, int] = {}

    def add(self, name: str, score: int) -> None:
        if name in self._scores:
            self.remove(name)
        self._scores[name] = score
        insort(self._entries, (-score, name))

    def remove(self, name: str) -> None:
        old = self._scores.pop(name)
        index = bisect_left(self._entries, (-old, name))
        del self._entries[index]

    def top(self, n: int) -> list[tuple[str, int]]:
        if n <= 0:
            return []
        return [(name, -neg) for neg, name in self._entries[:n]]

    def rank(self, name: str) -> int:
        score = self._scores[name]
        return bisect_left(self._entries, -score, key=_first) + 1

    def count_at_least(self, score: int) -> int:
        return bisect_right(self._entries, -score, key=_first)

    def __len__(self) -> int:
        return len(self._entries)
