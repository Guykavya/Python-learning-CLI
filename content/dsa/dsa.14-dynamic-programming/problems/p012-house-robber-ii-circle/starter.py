def rob_circle(nums):
    """Most money from houses in a circle (first and last are neighbours), never two neighbours."""
    prev2, prev1 = 0, 0
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1
