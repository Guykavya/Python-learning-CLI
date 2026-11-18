def max_product(nums):
    """Largest product of a non-empty contiguous block."""
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur * x)
        best = max(best, cur)
    return best
