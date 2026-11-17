import heapq


def k_closest(points, k):
    if k <= 0:
        return []
    heap = []
    for point in points:
        x, y = point
        entry = (-(x * x + y * y), -x, -y)
        if len(heap) < k:
            heapq.heappush(heap, entry)
        elif entry > heap[0]:
            heapq.heapreplace(heap, entry)
    best = sorted((-nd, -nx, -ny) for nd, nx, ny in heap)
    return [(x, y) for _, x, y in best]
