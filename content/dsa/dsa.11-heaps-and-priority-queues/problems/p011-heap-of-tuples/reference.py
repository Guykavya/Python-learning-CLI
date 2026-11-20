import heapq
import itertools


class TaskQueue:
    def __init__(self):
        self._heap = []
        self._counter = itertools.count()

    def add(self, priority, task):
        heapq.heappush(self._heap, (priority, next(self._counter), task))

    def pop(self):
        _, _, task = heapq.heappop(self._heap)
        return task

    def __len__(self):
        return len(self._heap)
