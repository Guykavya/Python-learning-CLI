import heapq


def top_scores(scores, k):
    if k <= 0:
        return []
    heap = []
    for s in scores:
        if len(heap) < k:
            heapq.heappush(heap, s)
        elif s > heap[0]:
            heapq.heapreplace(heap, s)
    return sorted(heap, reverse=True)
