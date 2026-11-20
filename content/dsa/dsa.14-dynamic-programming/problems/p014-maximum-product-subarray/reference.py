def max_product(nums):
    hi = lo = best = nums[0]          # largest and smallest product ending here
    for x in nums[1:]:
        candidates = (x, hi * x, lo * x)
        hi, lo = max(candidates), min(candidates)
        if hi > best:
            best = hi
    return best
