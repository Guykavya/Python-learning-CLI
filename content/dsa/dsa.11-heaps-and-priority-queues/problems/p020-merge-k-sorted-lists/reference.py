import heapq


def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    result = []
    while heap:
        value, i, j = heap[0]
        result.append(value)
        if j + 1 < len(lists[i]):
            heapq.heapreplace(heap, (lists[i][j + 1], i, j + 1))
        else:
            heapq.heappop(heap)
    return result
