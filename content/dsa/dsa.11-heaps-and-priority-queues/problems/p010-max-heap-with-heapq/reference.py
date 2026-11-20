import heapq


class MaxHeap:
    def __init__(self, items=()):
        self._h = [-x for x in items]
        heapq.heapify(self._h)

    def push(self, x):
        heapq.heappush(self._h, -x)

    def pop(self):
        return -heapq.heappop(self._h)

    def peek(self):
        return -self._h[0]

    def __len__(self):
        return len(self._h)
