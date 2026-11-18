def can_jump(nums):
    farthest = 0
    for i, jump in enumerate(nums):
        if i > farthest:
            return False                       # a gap: nothing reaches i
        farthest = max(farthest, i + jump)
    return True
