import heapq


def top_scores(scores, k):
    """The k highest scores, highest first. A classmate's version: it has two bugs."""
    heap = []                              # a max-heap by negation, at most k scores
    for s in scores:
        if len(heap) < k:
            heapq.heappush(heap, -s)
        elif -s > heap[0]:                 # better than the worst kept score?
            heapq.heapreplace(heap, -s)
    return sorted((-v for v in heap), reverse=True)
