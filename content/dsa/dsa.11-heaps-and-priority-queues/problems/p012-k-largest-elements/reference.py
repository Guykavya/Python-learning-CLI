import heapq


def k_largest(nums, k):
    if k <= 0:
        return []
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
    result = [heapq.heappop(heap) for _ in range(len(heap))]
    result.reverse()
    return result
