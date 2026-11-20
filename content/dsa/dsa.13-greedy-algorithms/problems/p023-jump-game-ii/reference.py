def min_jumps(nums):
    jumps = 0
    layer_end = 0          # furthest index reachable with `jumps` jumps
    farthest = 0           # furthest index reachable with `jumps + 1` jumps
    for i in range(len(nums) - 1):
        farthest = max(farthest, i + nums[i])
        if i == layer_end:             # must jump now to go further
            jumps += 1
            layer_end = farthest
    return jumps
