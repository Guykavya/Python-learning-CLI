def next_greater(nums):
    ans = [-1] * len(nums)
    waiting = []
    for i, x in enumerate(nums):
        while waiting and nums[waiting[-1]] < x:
            ans[waiting.pop()] = x
        waiting.append(i)
    return ans
