def smaller_after(nums):
    """out[i] = number of j > i with nums[j] < nums[i]."""
    return [sum(1 for y in nums[i + 1:] if y < x) for i, x in enumerate(nums)]      # O(n**2)
