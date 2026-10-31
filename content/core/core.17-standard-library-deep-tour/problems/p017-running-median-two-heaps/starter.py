import heapq
from collections.abc import Iterable


class MedianKeeper:
    def __init__(self) -> None:
        self._low: list[float] = []   # max-heap of the smaller half, values negated
        self._high: list[float] = []  # min-heap of the larger half

    def add(self, x: float) -> None:
        pass

    def median(self) -> float:
        raise ValueError("not written yet")

    def __len__(self) -> int:
        return 0


def running_medians(nums: Iterable[float]) -> list[float]:
    return []
