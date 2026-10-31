from bisect import bisect_left, bisect_right, insort


class Leaderboard:
    def __init__(self) -> None:
        self._entries: list[tuple[int, str]] = []
        self._scores: dict[str, int] = {}

    def add(self, name: str, score: int) -> None:
        pass

    def remove(self, name: str) -> None:
        pass

    def top(self, n: int) -> list[tuple[str, int]]:
        return []

    def rank(self, name: str) -> int:
        return 0

    def count_at_least(self, score: int) -> int:
        return 0

    def __len__(self) -> int:
        return 0
