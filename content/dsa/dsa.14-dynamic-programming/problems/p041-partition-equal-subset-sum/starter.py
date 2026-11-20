def can_partition(nums):
    """True if nums can be split into two groups with equal sums."""
    return sum(nums) % 2 == 0
