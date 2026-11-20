import heapq
from collections import Counter


def reorganize(s):
    heap = [(-count, letter) for letter, count in Counter(s).items()]
    heapq.heapify(heap)
    result = []
    held = (0, "")
    while heap:
        count, letter = heapq.heappop(heap)
        result.append(letter)
        if held[0] < 0:
            heapq.heappush(heap, held)
        held = (count + 1, letter)
    return "".join(result) if len(result) == len(s) else ""
