import heapq


class MedianFinder:
    def __init__(self):
        self.low = []                                  # max-heap, stored as negatives
        self.high = []                                 # min-heap

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def median(self):
        if not self.low:
            raise ValueError("no numbers yet")
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2
