import heapq


def kth_smallest(matrix, k):
    n, m = len(matrix), len(matrix[0])
    heap = [(matrix[r][0], r, 0) for r in range(min(n, k))]
    heapq.heapify(heap)
    for _ in range(k - 1):
        value, r, c = heapq.heappop(heap)
        if c + 1 < m:
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return heap[0][0]
