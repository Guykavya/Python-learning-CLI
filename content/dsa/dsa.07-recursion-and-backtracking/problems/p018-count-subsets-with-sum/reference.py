def count_subsets(nums, target):
    def go(i, remaining):
        if remaining == 0:
            return 1
        if remaining < 0 or i == len(nums):
            return 0
        return go(i + 1, remaining - nums[i]) + go(i + 1, remaining)

    return go(0, target)
