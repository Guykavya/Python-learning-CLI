import time
from collections.abc import Callable


class Stopwatch:
    def __init__(self, clock: Callable[[], float] = time.perf_counter) -> None:
        self.clock = clock
        self._start: float | None = None
        self._laps: list[float] = []
        self._last: float = 0.0

    def start(self) -> None:
        if self._start is not None:
            raise RuntimeError("the stopwatch is already running")
        self._start = self.clock()
        self._last = self._start
        self._laps = []

    def lap(self) -> float:
        if self._start is None:
            raise RuntimeError("start() the stopwatch first")
        now = self.clock()
        split = now - self._last
        self._last = now
        self._laps.append(split)
        return split

    def stop(self) -> float:
        if self._start is None:
            raise RuntimeError("start() the stopwatch first")
        total = self.clock() - self._start
        self._start = None
        return total

    @property
    def laps(self) -> list[float]:
        return list(self._laps)


class Deadline:
    def __init__(self, seconds: float, clock: Callable[[], float] = time.monotonic) -> None:
        if seconds < 0:
            raise ValueError("seconds must not be negative")
        self.clock = clock
        self._end = clock() + seconds

    def remaining(self) -> float:
        return max(0.0, self._end - self.clock())

    def expired(self) -> bool:
        return self.clock() >= self._end


def timed(func: Callable[[], object], clock: Callable[[], float] = time.perf_counter) -> tuple[object, float]:
    start = clock()
    result = func()
    return result, clock() - start
