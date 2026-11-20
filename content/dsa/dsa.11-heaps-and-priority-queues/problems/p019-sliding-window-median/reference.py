import heapq


def sliding_median(nums, k):
    n = len(nums)
    if k < 1 or k > n:
        return []
    low, high = [], []                 # low: (-value, index) max-heap, high: (value, index) min-heap
    side = [2] * n                     # 0 = live in low, 1 = live in high, 2 = not in a heap (or already removed)
    lo_n = hi_n = 0                    # number of LIVE entries in each heap

    def prune():
        while low and side[low[0][1]] != 0:
            heapq.heappop(low)
        while high and side[high[0][1]] != 1:
            heapq.heappop(high)

    out = []
    for i, x in enumerate(nums):
        prune()
        if low and x > -low[0][0]:
            heapq.heappush(high, (x, i))
            side[i] = 1
            hi_n += 1
        else:
            heapq.heappush(low, (-x, i))
            side[i] = 0
            lo_n += 1
        if i >= k:                     # the number nums[i - k] leaves the window
            j = i - k
            if side[j] == 0:
                lo_n -= 1
            else:
                hi_n -= 1
            side[j] = 2                # lazy deletion: its entry stays in a heap until it reaches the top
        while lo_n > hi_n + 1:
            prune()
            value, j = heapq.heappop(low)
            heapq.heappush(high, (-value, j))
            side[j] = 1
            lo_n -= 1
            hi_n += 1
        while lo_n < hi_n:
            prune()
            value, j = heapq.heappop(high)
            heapq.heappush(low, (-value, j))
            side[j] = 0
            hi_n -= 1
            lo_n += 1
        if i >= k - 1:
            prune()
            if k % 2:
                out.append(-low[0][0])
            else:
                out.append((-low[0][0] + high[0][0]) / 2)
    return out
