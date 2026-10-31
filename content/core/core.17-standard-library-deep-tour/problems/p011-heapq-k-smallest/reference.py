import heapq
from collections.abc import Iterable


def k_smallest(nums: Iterable[int], k: int) -> list[int]:
    if k <= 0:
        return []
    return heapq.nsmallest(k, nums)


def top_k_by(records: list[dict], k: int, field: str) -> list[dict]:
    if k <= 0:
        return []
    return heapq.nlargest(k, records, key=lambda record: record[field])


def pop_k_smallest(nums: list[int], k: int) -> list[int]:
    heap = list(nums)
    heapq.heapify(heap)
    result = []
    while heap and len(result) < k:
        result.append(heapq.heappop(heap))
    return result
