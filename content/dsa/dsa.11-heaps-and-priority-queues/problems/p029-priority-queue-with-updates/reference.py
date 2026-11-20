import heapq
import itertools


class LazyPQ:
    REMOVED = object()

    def __init__(self):
        self.heap = []
        self.entries = {}
        self.counter = itertools.count()

    def add(self, task, priority):
        if task in self.entries:
            self.entries[task][-1] = self.REMOVED
        entry = [priority, next(self.counter), task]
        self.entries[task] = entry
        heapq.heappush(self.heap, entry)
        self._compact_if_needed()

    def remove(self, task):
        entry = self.entries.pop(task)
        entry[-1] = self.REMOVED
        self._compact_if_needed()

    def pop(self):
        while self.heap:
            priority, _, task = heapq.heappop(self.heap)
            if task is not self.REMOVED:
                del self.entries[task]
                self._compact_if_needed()
                return task
        raise KeyError("pop from an empty priority queue")

    def __len__(self):
        return len(self.entries)

    def __contains__(self, task):
        return task in self.entries

    def stored(self):
        return len(self.heap)

    def _compact_if_needed(self):
        if len(self.heap) > 2 * len(self.entries) + 8:
            self.heap = list(self.entries.values())
            heapq.heapify(self.heap)
