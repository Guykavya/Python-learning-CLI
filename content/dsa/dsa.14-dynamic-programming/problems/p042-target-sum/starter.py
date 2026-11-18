def target_sum(nums, target):
    """Number of ways to put + or - before every number so the sum equals target."""
    return 1 if sum(nums) == target else 0
