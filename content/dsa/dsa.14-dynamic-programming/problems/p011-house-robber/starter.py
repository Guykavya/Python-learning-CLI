def rob(nums):
    """Most money from houses in a row, never robbing two neighbours."""
    return sum(nums[::2])
