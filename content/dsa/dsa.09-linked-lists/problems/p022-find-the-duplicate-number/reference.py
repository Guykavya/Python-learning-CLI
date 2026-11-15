def find_duplicate(nums):
    slow = fast = 0
    while True:                          # phase 1: meet inside the cycle
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    p = 0
    while p != slow:                     # phase 2: the entrance of the cycle
        p = nums[p]
        slow = nums[slow]
    return p
