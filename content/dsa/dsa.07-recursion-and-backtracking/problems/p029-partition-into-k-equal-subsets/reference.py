def can_partition_k(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False
    side = total // k
    nums = sorted(nums, reverse=True)
    if nums[0] > side:
        return False
    buckets = [0] * k

    def go(i):
        if i == len(nums):
            return True
        tried = set()
        for b in range(k):
            if buckets[b] + nums[i] > side or buckets[b] in tried:
                continue
            tried.add(buckets[b])
            buckets[b] += nums[i]
            if go(i + 1):
                return True
            buckets[b] -= nums[i]
        return False

    return go(0)
