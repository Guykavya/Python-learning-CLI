def max_subarray(nums):
    cur = best = nums[0]             # f(0), and the best so far
    for x in nums[1:]:
        cur = max(x, cur + x)        # f(i) = max(nums[i], f(i-1) + nums[i])
        if cur > best:
            best = cur
    return best
