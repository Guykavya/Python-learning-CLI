import time
from collections.abc import Callable


class Stopwatch:
    def __init__(self, clock: Callable[[], float] = time.time) -> None:
        self.clock = clock

    def start(self) -> None:
        pass

    def lap(self) -> float:
        return 0.0

    def stop(self) -> float:
        return 0.0

    @property
    def laps(self) -> list[float]:
        return []


class Deadline:
    def __init__(self, seconds: float, clock: Callable[[], float] = time.time) -> None:
        self.clock = clock

    def remaining(self) -> float:
        return 0.0

    def expired(self) -> bool:
        return False


def timed(func: Callable[[], object], clock: Callable[[], float] = time.time) -> tuple[object, float]:
    return func(), 0.0
