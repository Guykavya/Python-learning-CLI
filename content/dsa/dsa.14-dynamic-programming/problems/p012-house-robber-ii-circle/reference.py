def rob_row(houses):
    prev2, prev1 = 0, 0
    for money in houses:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1


def rob_circle(nums):
    if len(nums) == 1:
        return nums[0]
    return max(rob_row(nums[:-1]), rob_row(nums[1:]))
