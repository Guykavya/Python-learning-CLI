def largest_number(nums):
    """Arrange the numbers to form the largest number; return it as a string."""
    return "".join(str(x) for x in sorted(nums, reverse=True))
