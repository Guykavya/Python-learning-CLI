import heapq
import itertools


class TaskQueue:
    def __init__(self) -> None:
        self._heap: list[tuple[int, int, object]] = []
        self._counter = itertools.count()

    def push(self, task, priority: int) -> None:
        heapq.heappush(self._heap, (priority, next(self._counter), task))

    def pop(self):
        if not self._heap:
            raise IndexError("pop from an empty TaskQueue")
        return heapq.heappop(self._heap)[2]

    def peek(self):
        if not self._heap:
            raise IndexError("peek at an empty TaskQueue")
        return self._heap[0][2]

    def __len__(self) -> int:
        return len(self._heap)

    def __bool__(self) -> bool:
        return len(self._heap) > 0
