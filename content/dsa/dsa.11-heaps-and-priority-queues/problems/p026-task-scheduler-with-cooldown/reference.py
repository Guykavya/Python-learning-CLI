import heapq
from collections import Counter, deque


def least_interval(tasks, n):
    heap = [-count for count in Counter(tasks).values()]
    heapq.heapify(heap)
    cooling = deque()
    time = 0
    while heap or cooling:
        time += 1
        while cooling and cooling[0][0] <= time:
            heapq.heappush(heap, cooling.popleft()[1])
        if heap:
            remaining = heapq.heappop(heap) + 1
            if remaining < 0:
                cooling.append((time + n + 1, remaining))
    return time
