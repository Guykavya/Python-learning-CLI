import heapq


def minimum_effort(heights):
    rows, cols = len(heights), len(heights[0])
    INF = float("inf")
    best = [[INF] * cols for _ in range(rows)]
    best[0][0] = 0
    heap = [(0, 0, 0)]
    while heap:
        e, r, c = heapq.heappop(heap)
        if (r, c) == (rows - 1, cols - 1):
            return e
        if e > best[r][c]:
            continue
        for nr, nc in ((r - 1, c), (r + 1, c), (r, c - 1), (r, c + 1)):
            if 0 <= nr < rows and 0 <= nc < cols:
                ne = max(e, abs(heights[r][c] - heights[nr][nc]))
                if ne < best[nr][nc]:
                    best[nr][nc] = ne
                    heapq.heappush(heap, (ne, nr, nc))
    return 0
