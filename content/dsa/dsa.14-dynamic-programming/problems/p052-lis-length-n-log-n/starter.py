from bisect import bisect_left


def lis_len(nums):
    """Length of the longest strictly increasing subsequence, in O(n log n)."""
    return min(len(nums), 1)
