def has_subset_sum(nums, target):
    def go(i, remaining):
        if remaining == 0:
            return True
        if i == len(nums):
            return False
        return go(i + 1, remaining - nums[i]) or go(i + 1, remaining)

    return go(0, target)
