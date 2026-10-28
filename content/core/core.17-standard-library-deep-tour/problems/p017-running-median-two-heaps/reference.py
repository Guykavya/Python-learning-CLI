import heapq
from collections.abc import Iterable


class MedianKeeper:
    def __init__(self) -> None:
        self._low: list[float] = []   # max-heap of the smaller half, values negated
        self._high: list[float] = []  # min-heap of the larger half

    def add(self, x: float) -> None:
        if not self._low or x <= -self._low[0]:
            heapq.heappush(self._low, -x)
        else:
            heapq.heappush(self._high, x)
        if len(self._low) > len(self._high) + 1:
            heapq.heappush(self._high, -heapq.heappop(self._low))
        elif len(self._high) > len(self._low):
            heapq.heappush(self._low, -heapq.heappop(self._high))

    def median(self) -> float:
        if not self._low:
            raise ValueError("median of an empty MedianKeeper")
        if len(self._low) > len(self._high):
            return -self._low[0]
        return (-self._low[0] + self._high[0]) / 2

    def __len__(self) -> int:
        return len(self._low) + len(self._high)


def running_medians(nums: Iterable[float]) -> list[float]:
    keeper = MedianKeeper()
    result = []
    for x in nums:
        keeper.add(x)
        result.append(keeper.median())
    return result
