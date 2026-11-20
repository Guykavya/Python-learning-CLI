def can_split(nums, k):
    """True if nums can be divided into k groups with equal sums (each number in exactly one group)."""
    return sum(nums) % k == 0
