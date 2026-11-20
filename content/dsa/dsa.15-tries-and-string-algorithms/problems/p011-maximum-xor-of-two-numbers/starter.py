def max_xor(nums):
    """Largest a ^ b over two entries of nums (0 for a single number)."""
    return max(nums) ^ min(nums)
