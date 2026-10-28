import heapq
import itertools


class TaskQueue:
    def __init__(self) -> None:
        self._heap: list = []

    def push(self, task, priority: int) -> None:
        pass

    def pop(self):
        raise IndexError("not written yet")

    def peek(self):
        raise IndexError("not written yet")

    def __len__(self) -> int:
        return 0

    def __bool__(self) -> bool:
        return False
